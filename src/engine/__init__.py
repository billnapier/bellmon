"""
Engine package for Bellmon academic sentinel logic.
"""

from src.engine.models import (
    AssignmentStatus,
    AlertSource,
    CanvasAssignmentInput,
    PowerSchoolAssignmentInput,
    PendingMissingAlert,
    PendingGradeDropAlert,
    CourseVelocityInput,
    StudentVelocityContext,
    AttendanceCodeSeverity,
    AttendanceRecordInput,
    AttendanceEvent,
    PendingAttendanceAlert,
)
from src.engine.authority import AsymmetricAuthorityEngine
from src.engine.velocity import GradeVelocityEngine
from src.engine.attendance import AttendanceSentinel

__all__ = [
    "AssignmentStatus",
    "AlertSource",
    "CanvasAssignmentInput",
    "PowerSchoolAssignmentInput",
    "PendingMissingAlert",
    "PendingGradeDropAlert",
    "CourseVelocityInput",
    "StudentVelocityContext",
    "AttendanceCodeSeverity",
    "AttendanceRecordInput",
    "AttendanceEvent",
    "PendingAttendanceAlert",
    "AsymmetricAuthorityEngine",
    "GradeVelocityEngine",
    "AttendanceSentinel",
]
