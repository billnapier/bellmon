"""
Canvas LMS REST API Ingestion Client module.

Leverages standard open-source HTTP libraries (requests, urllib3) and Pydantic schema validation
to interact directly with official Canvas LMS REST API observer endpoints (Principle 6 Compliance).
"""

import os
import logging
from typing import List, Optional
from datetime import datetime
import requests
from urllib3.util import Retry
from requests.adapters import HTTPAdapter
from pydantic import BaseModel, Field

logger = logging.getLogger("bellmon.canvas")


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
