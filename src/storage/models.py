"""
Data models for Bellmon student academic state persistence in GCP Cloud Firestore.
"""

from enum import Enum
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, timezone
from pydantic import BaseModel, Field, model_validator


class GradeSnapshot(BaseModel):
    """Snapshot of a student's grade in a specific course at a given date."""
    date: str  # Format: YYYY-MM-DD
    percentage: float
    letter_grade: str


class CourseState(BaseModel):
    """Academic course state including current grades and historical snapshots."""
    name: str
    current_percentage: float
    letter_grade: str
    history: List[GradeSnapshot] = Field(default_factory=list)


class TrackedAssignment(BaseModel):
    """Assignment tracked by Canvas ingestion engine for missing/grace period alert management."""
    title: str
    course_id: str
    due_at: str  # ISO format string
    submission_type: str
    status: str = "missing"  # Options: missing, submitted, graded, grace_period
    first_detected_missing: Optional[str] = None  # ISO format string
    alert_dispatched: bool = False


class AttendanceCodeSeverity(str, Enum):
    """Severity classification for period attendance codes."""
    P0_URGENT = "P0_URGENT"  # Immediate alert (A, CUT)
    P1_DIGEST = "P1_DIGEST"  # Sunday digest queue (T, U)
    IGNORED = "IGNORED"      # No action (P, E, EX, ACT)


class AttendanceEvent(BaseModel):
    """Attendance anomaly event recorded from PowerSchool scraping."""
    date: str  # Format: YYYY-MM-DD
    period: Union[int, str]
    course_name: str = ""
    code: str  # Options: A, T, U, etc.
    description: Optional[str] = None
    severity: AttendanceCodeSeverity = AttendanceCodeSeverity.IGNORED
    notified: bool = False
    detected_at: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def populate_course_name(cls, data: Any):
        if isinstance(data, dict):
            if "course" in data and not data.get("course_name"):
                data["course_name"] = data["course"]
            elif "course_name" in data and not data.get("course"):
                data["course"] = data["course_name"]
        return data

    @property
    def course(self) -> str:
        return self.course_name


class SessionCookies(BaseModel):
    """Encrypted SAML session cookies for PowerSchool login reuse."""
    psaid: str
    updated_at: str  # ISO format string


class LateSubmissionRecord(BaseModel):
    """Record of a Canvas assignment submitted late."""
    assignment_id: str
    course_id: str
    course_name: str = ""
    title: str
    due_at: Optional[str] = None  # ISO format string
    submitted_at: Optional[str] = None  # ISO format string
    minutes_late: int = 0
    detected_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    is_late: bool = True


class DispatchedAlertRecord(BaseModel):
    """Ledger record for dispatched notifications/alerts."""
    alert_id: str
    alert_type: str  # e.g., "LATE_SUBMISSION_FREQUENCY_WARNING", "ATTENDANCE_P0"
    student_id: str
    dispatched_at: str  # ISO 8601 string
    metadata: Dict[str, Any] = Field(default_factory=dict)


class StudentState(BaseModel):
    """Master document structure stored at students/{student_id} in Firestore."""
    student_id: str
    last_synced_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    session_cookies: Optional[SessionCookies] = None
    courses: Dict[str, CourseState] = Field(default_factory=dict)
    tracked_assignments: Dict[str, TrackedAssignment] = Field(default_factory=dict)
    attendance_events: List[AttendanceEvent] = Field(default_factory=list)


class HeartbeatDispatchRecord(BaseModel):
    """Firestore record for tracking sent heartbeat briefings."""
    id: str
    student_name: str
    date: str
    dispatched_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    recipient: str
    message_id: Optional[str] = None
    status: str = "SUCCESS"


