from typing import Tuple, Optional
from src.storage.models import TrackedAssignment, SubmissionType, AssignmentState


class MissingWorkEvaluator:
    def evaluate(self, assignment: TrackedAssignment) -> Tuple[TrackedAssignment, bool, str]:
        """
        Evaluates missing work correlation matrix across Canvas and PowerSchool.
        Returns: (Updated TrackedAssignment, should_alert: bool, reason: str)
        """
        # Rule 1: Cross-System Paper / Graded Suppression (Principle 2)
        if assignment.powerschool_collected or (
            assignment.powerschool_score is not None and assignment.powerschool_score > 0
        ):
            assignment.state = AssignmentState.SUPPRESSED_PAPER_OR_GRADED
            return assignment, False, "SUPPRESSED_PAPER_OR_GRADED"

        # Rule 2: Confirmed PowerSchool Missing Direct Bypass (User Story 2)
        if assignment.powerschool_missing:
            assignment.state = AssignmentState.ALERT_DISPATCHED
            return assignment, True, "CONFIRMED_POWERSCHOOL_MISSING"

        if assignment.powerschool_score is not None and assignment.powerschool_score == 0.0:
            assignment.state = AssignmentState.ALERT_DISPATCHED
            return assignment, True, "CONFIRMED_POWERSCHOOL_ZERO"

        return assignment, False, "NO_ACTION"
