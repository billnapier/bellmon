from typing import Tuple, Optional
from src.config import settings
from src.storage.models import CourseSnapshot, TrackedAssignment


class VelocityDropEvaluator:
    def __init__(self, threshold: float = None):
        self.threshold = threshold or settings.grade_velocity_drop_threshold

    def evaluate(
        self,
        historical: Optional[CourseSnapshot],
        current: CourseSnapshot
    ) -> Tuple[bool, float, Optional[TrackedAssignment]]:
        """
        Calculates rolling 7-day course grade velocity drop.
        Returns: (should_alert: bool, drop_percentage: float, impacting_assignment)
        """
        if not historical:
            return False, 0.0, None

        drop = historical.current_score - current.current_score
        if drop < self.threshold:
            return False, drop, None

        # Isolate assignment responsible for score drop (lowest score or newly entered)
        impacting = None
        lowest_pct = 100.0
        for a in current.assignments:
            if a.powerschool_score is not None and a.points_possible > 0:
                pct = (a.powerschool_score / a.points_possible) * 100.0
                if pct < lowest_pct:
                    lowest_pct = pct
                    impacting = a

        return True, round(drop, 2), impacting
