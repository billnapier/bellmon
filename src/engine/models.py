"""
Data models and Enums for the Asymmetric System Authority Engine.
"""

from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


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
