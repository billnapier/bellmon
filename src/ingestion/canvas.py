"""
Canvas LMS REST API Ingestion Client module.

Leverages standard open-source HTTP libraries (requests, urllib3) and Pydantic schema validation
to interact directly with official Canvas LMS REST API observer endpoints (Principle 6 Compliance).
"""

import os
import logging
from typing import List, Optional
from datetime import datetime, timezone
import requests
from urllib3.util import Retry
from requests.adapters import HTTPAdapter
from pydantic import BaseModel, Field

from src.storage.models import LateSubmissionRecord

logger = logging.getLogger("bellmon.canvas")


def parse_iso_datetime(dt_str: Optional[str]) -> Optional[datetime]:
    """Parse an ISO 8601 datetime string, supporting 'Z' suffix."""
    if not dt_str:
        return None
    try:
        clean_str = dt_str.replace("Z", "+00:00")
        return datetime.fromisoformat(clean_str)
    except Exception as err:
        logger.warning(f"Could not parse datetime string '{dt_str}': {err}")
        return None


class CanvasCourse(BaseModel):
    id: int
    name: str
    course_code: Optional[str] = None


class CanvasAssignment(BaseModel):
    id: int
    name: str
    course_id: int
    due_at: Optional[datetime] = None
    points_possible: Optional[float] = 0.0
    submission_types: List[str] = Field(default_factory=list)
    has_submitted_submissions: bool = False
    missing: bool = True


class CanvasSubmission(BaseModel):
    """Raw Canvas Submission model returned by Canvas API."""
    id: Optional[int] = None
    assignment_id: int
    course_id: Optional[int] = None
    user_id: Optional[int] = None
    submitted_at: Optional[str] = None
    due_at: Optional[str] = None
    late: bool = False
    missing: bool = False
    excused: bool = False
    seconds_late: Optional[int] = 0
    workflow_state: Optional[str] = None
    assignment: Optional[dict] = None


class CanvasClient:
    """Canvas LMS REST API Client handling authentication, retries, and data parsing."""

    def __init__(self, base_url: str = "https://bcp.instructure.com", token: Optional[str] = None):
        self.base_url = os.getenv("CANVAS_BASE_URL", base_url).rstrip("/")
        self.token = token or self._resolve_token()
        self.session = self._create_session()

    def _resolve_token(self) -> str:
        """Resolves token from GCP Secret Manager or environment variable fallback."""
        token = os.getenv("CANVAS_API_TOKEN")
        if not token:
            try:
                from google.cloud import secretmanager
                client = secretmanager.SecretManagerServiceClient()
                project_id = os.getenv("GCP_PROJECT") or os.getenv("GOOGLE_CLOUD_PROJECT") or "bellmon"
                name = f"projects/{project_id}/secrets/canvas-api-token/versions/latest"
                response = client.access_secret_version(request={"name": name})
                token = response.payload.data.decode("UTF-8")
            except Exception as err:
                logger.warning(f"Could not resolve token from GCP Secret Manager: {err}")
        if not token:
            logger.info("Using empty dummy token for Canvas client initialization.")
            token = "dummy_token"
        return token

    def _create_session(self) -> requests.Session:
        session = requests.Session()
        retry_strategy = Retry(
            total=1,
            backoff_factor=0.5,
            status_forcelist=[429],
            allowed_methods=["GET"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        session.headers.update({
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        })
        return session

    def get_courses(self) -> List[CanvasCourse]:
        """Fetch active enrolled courses for observee."""
        url = f"{self.base_url}/api/v1/courses"
        resp = self.session.get(url, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        return [CanvasCourse.model_validate(c) for c in data if isinstance(c, dict) and "id" in c]

    def get_missing_submissions(self, observee_id: str = "self") -> List[CanvasAssignment]:
        """Fetch missing digital submissions for observee."""
        url = f"{self.base_url}/api/v1/users/{observee_id}/missing_submissions"
        resp = self.session.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        # Handle object format or list format in Canvas API response
        assignments_raw = data if isinstance(data, list) else data.get("missing_submissions", [])
        assignments = []
        for item in assignments_raw:
            if isinstance(item, dict) and "id" in item:
                assignments.append(CanvasAssignment.model_validate(item))
        return assignments

    def get_student_submissions(
        self, observee_id: str = "self", course_id: Optional[str] = None
    ) -> List[CanvasSubmission]:
        """Fetch assignment submissions for observee, optionally scoped by course_id."""
        if course_id:
            url = f"{self.base_url}/api/v1/users/{observee_id}/courses/{course_id}/submissions"
        else:
            url = f"{self.base_url}/api/v1/users/{observee_id}/submissions"
        
        resp = self.session.get(url, params={"include[]": "assignment"}, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        submissions_raw = data if isinstance(data, list) else data.get("submissions", [])
        submissions = []
        for item in submissions_raw:
            if isinstance(item, dict) and "assignment_id" in item:
                submissions.append(CanvasSubmission.model_validate(item))
        return submissions

    def process_late_submissions(
        self,
        student_id: str,
        submissions: List[CanvasSubmission],
        course_names: Optional[dict] = None,
    ) -> List[LateSubmissionRecord]:
        """
        Process CanvasSubmission items into LateSubmissionRecord objects.
        Evaluates late flag, computes minutes_late, handles due date updates/extensions.
        """
        course_names = course_names or {}
        late_records: List[LateSubmissionRecord] = []
        now_iso = datetime.now(timezone.utc).isoformat()

        for sub in submissions:
            sub_dt = parse_iso_datetime(sub.submitted_at)
            due_dt = parse_iso_datetime(sub.due_at)

            # Check if assignment metadata carries due_at if submission doesn't
            if not due_dt and sub.assignment and isinstance(sub.assignment, dict):
                due_dt = parse_iso_datetime(sub.assignment.get("due_at"))
                if not sub.due_at and sub.assignment.get("due_at"):
                    sub.due_at = sub.assignment.get("due_at")

            # Re-evaluate late status if due date was extended
            was_flagged_late = sub.late
            is_late = sub.late
            if sub_dt and due_dt:
                if sub_dt > due_dt:
                    is_late = True
                else:
                    # Due date extended post-submission
                    is_late = False

            if not is_late and not was_flagged_late:
                continue

            # Compute minutes_late
            minutes_late = 0
            if is_late:
                if sub.seconds_late and sub.seconds_late > 0:
                    minutes_late = max(0, sub.seconds_late // 60)
                elif sub_dt and due_dt and sub_dt > due_dt:
                    minutes_late = int((sub_dt - due_dt).total_seconds() // 60)

            # Determine assignment title and course name
            title = f"Assignment {sub.assignment_id}"
            if sub.assignment and isinstance(sub.assignment, dict):
                title = sub.assignment.get("name") or title

            c_id = str(sub.course_id or "")
            c_name = course_names.get(c_id, f"Course {c_id}" if c_id else "")

            rec = LateSubmissionRecord(
                assignment_id=str(sub.assignment_id),
                course_id=c_id,
                course_name=c_name,
                title=title,
                due_at=sub.due_at,
                submitted_at=sub.submitted_at,
                minutes_late=minutes_late,
                detected_at=now_iso,
                is_late=is_late,
            )
            late_records.append(rec)

        return late_records

