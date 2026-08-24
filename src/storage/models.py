"""
Data models for Bellmon student academic state persistence in GCP Cloud Firestore.
"""

from typing import Dict, List, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field


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


class AttendanceEvent(BaseModel):
    """Attendance anomaly event recorded from PowerSchool scraping."""
    date: str  # Format: YYYY-MM-DD
    period: str
    course: str
    code: str  # Options: A, T, U, etc.
    notified: bool = False


class SessionCookies(BaseModel):
    """Encrypted SAML session cookies for PowerSchool login reuse."""
    psaid: str
    updated_at: str  # ISO format string


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
