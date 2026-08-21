from datetime import datetime, timezone
from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field


class SubmissionType(str, Enum):
    ONLINE_UPLOAD = "online_upload"
    PAPER = "paper"
    EXTERNAL_TOOL = "external_tool"
    DISCUSSION = "discussion"
    NONE = "none"


class AssignmentState(str, Enum):
    NEW = "NEW"
    GRACE_PERIOD = "GRACE_PERIOD"
    ALERT_DISPATCHED = "ALERT_DISPATCHED"
    SUPPRESSED_PAPER_OR_GRADED = "SUPPRESSED_PAPER_OR_GRADED"
    RESOLVED = "RESOLVED"


class TrackedAssignment(BaseModel):
    assignment_id: str
    course_id: str
    title: str
    due_at: Optional[datetime] = None
    submission_type: SubmissionType = SubmissionType.NONE
    points_possible: float = 0.0

    # Canvas & PowerSchool state flags
    canvas_missing: bool = False
    powerschool_missing: bool = False
    powerschool_score: Optional[float] = None
    powerschool_collected: bool = False

    # Sentinel State Machine
    state: AssignmentState = AssignmentState.NEW
    first_detected_overdue: Optional[datetime] = None
    last_evaluated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AttendanceEvent(BaseModel):
    event_id: str
    student_id: str
    date: str  # YYYY-MM-DD
    period: str
    code: str  # A, T, U, CUT, P
    description: str
    is_unexcused: bool = False


class CourseSnapshot(BaseModel):
    course_id: str
    course_name: str
    teacher_name: str
    current_score: float
    grade_letter: str
    assignments: List[TrackedAssignment] = Field(default_factory=list)
    recorded_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Student(BaseModel):
    student_id: str
    name: str
    courses: List[CourseSnapshot] = Field(default_factory=list)
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
