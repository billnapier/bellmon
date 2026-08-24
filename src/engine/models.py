"""
Data models and Enums for the Asymmetric System Authority Engine.
"""

from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field
from src.storage.models import GradeSnapshot, AttendanceCodeSeverity, AttendanceEvent


class AssignmentStatus(str, Enum):
    """Status enum for tracked assignment state machine."""
    NEW = "NEW"
    GRACE_PERIOD = "GRACE_PERIOD"
    EXPIRED = "EXPIRED"
    CONFIRMED_MISSING = "CONFIRMED_MISSING"
    RESOLVED = "RESOLVED"
    SUPPRESSED = "SUPPRESSED"


class AlertSource(str, Enum):
    """Source classification for pending missing alerts."""
    CANVAS_GRACE_EXPIRED = "CANVAS_GRACE_EXPIRED"
    POWERSCHOOL_CONFIRMED = "POWERSCHOOL_CONFIRMED"


class CanvasAssignmentInput(BaseModel):
    """Input payload representing a Canvas assignment state."""
    assignment_id: str
    title: str
    course_id: str
    due_at: str  # ISO timestamp
    submission_types: List[str] = Field(default_factory=list)
    is_missing: bool = False


class PowerSchoolAssignmentInput(BaseModel):
    """Input payload representing a PowerSchool assignment record."""
    assignment_id: str
    title: str
    course_id: str
    due_at: Optional[str] = None
    is_missing: bool = False
    score: Optional[float] = None
    points_possible: Optional[float] = None


class PendingMissingAlert(BaseModel):
    """Structured alert record queued for notification dispatch."""
    assignment_id: str
    title: str
    course_id: str
    due_at: Optional[str] = None
    source: AlertSource
    points_possible: Optional[float] = None
    detected_at: str  # ISO timestamp


class PendingGradeDropAlert(BaseModel):
    """Structured alert record for a detected grade velocity drop (>= 4.0%)."""
    course_id: str
    course_name: str
    prev_percentage: float
    curr_percentage: float
    delta: float
    detected_at: str  # ISO timestamp


class CourseVelocityInput(BaseModel):
    """Input parameters for course velocity drop evaluation."""
    course_id: str
    course_name: str
    current_percentage: float
    history: List[GradeSnapshot] = Field(default_factory=list)
    total_graded_points: Optional[float] = None
    term_active_days: Optional[int] = None


class StudentVelocityContext(BaseModel):
    """Context holding student registration and history tracking information for silent warming protocol."""
    student_id: str
    tracking_start_date: str  # Format: YYYY-MM-DD or ISO timestamp
    courses: List[CourseVelocityInput] = Field(default_factory=list)


class AttendanceRecordInput(BaseModel):
    """Raw attendance record harvested from PowerSchool."""
    date: str             # Format: YYYY-MM-DD
    period: int           # Class period number (e.g. 1, 2, 3)
    course_name: str      # Name of the course (e.g. "Algebra II")
    code: str             # Attendance code (e.g. "A", "CUT", "T", "U", "P", "E")
    description: Optional[str] = None


class PendingAttendanceAlert(BaseModel):
    """Payload for P0 urgent attendance email alert."""
    student_id: str
    date: str
    period: int
    course_name: str
    code: str
    description: str
    severity: AttendanceCodeSeverity = AttendanceCodeSeverity.P0_URGENT
    detected_at: str      # ISO timestamp


