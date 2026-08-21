from datetime import datetime, timedelta, timezone
from typing import Tuple
from src.config import settings
from src.storage.models import TrackedAssignment, SubmissionType, AssignmentState


class GracePeriodEvaluator:
    def __init__(self, grace_period_hours: float = None):
        self.grace_period_hours = grace_period_hours or settings.grace_period_hours

    def evaluate(
        self,
        assignment: TrackedAssignment,
        current_time: datetime = None
    ) -> Tuple[TrackedAssignment, bool]:
        """
        Evaluates mandatory 36-hour grace period for digital upload assignments.
        Returns: (Updated TrackedAssignment, should_alert: bool)
        """
        now = current_time or datetime.now(timezone.utc)
        assignment.last_evaluated_at = now

        # If assignment is no longer missing in Canvas, mark resolved
        if not assignment.canvas_missing:
            if assignment.state in (AssignmentState.NEW, AssignmentState.GRACE_PERIOD):
                assignment.state = AssignmentState.RESOLVED
            return assignment, False

        # Only online_upload assignments are eligible for grace period
        if assignment.submission_type != SubmissionType.ONLINE_UPLOAD:
            return assignment, False

        # First detection -> transition to GRACE_PERIOD
        if assignment.state == AssignmentState.NEW or assignment.first_detected_overdue is None:
            assignment.state = AssignmentState.GRACE_PERIOD
            assignment.first_detected_overdue = now
            return assignment, False

        # If already in GRACE_PERIOD, check threshold
        if assignment.state == AssignmentState.GRACE_PERIOD:
            elapsed_hours = (now - assignment.first_detected_overdue).total_seconds() / 3600.0
            if elapsed_hours >= self.grace_period_hours:
                assignment.state = AssignmentState.ALERT_DISPATCHED
                return assignment, True  # Post-36h alert trigger
            return assignment, False

        return assignment, False
