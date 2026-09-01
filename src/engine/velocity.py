"""
Grade Velocity Drop (>= 4.0%) Sentinel & Silent Warming Engine.
"""

from datetime import date, datetime, timezone
from typing import List, Optional, Union
from src.engine.models import (
    CourseVelocityInput,
    PendingGradeDropAlert,
    StudentVelocityContext,
)
from src.storage.models import GradeSnapshot, StudentPreferences


class GradeVelocityEngine:
    """Evaluates student academic course grade velocity drops and suppresses noisy or un-warmed alerts."""

    def __init__(
        self,
        drop_threshold: float = 4.0,
        preferences: Optional[StudentPreferences] = None,
    ):
        if preferences is not None:
            self.drop_threshold = preferences.velocity_drop_threshold
        else:
            self.drop_threshold = drop_threshold
        self.preferences = preferences

    def _parse_date(self, date_val: Union[str, date]) -> date:
        """Helper to convert string or date object to datetime.date."""
        if isinstance(date_val, date) and not isinstance(date_val, datetime):
            return date_val
        if isinstance(date_val, datetime):
            return date_val.date()
        if isinstance(date_val, str):
            # Try YYYY-MM-DD format first
            try:
                return datetime.strptime(date_val[:10], "%Y-%m-%d").date()
            except ValueError:
                return datetime.fromisoformat(date_val).date()
        raise ValueError(f"Invalid date format: {date_val}")

    def is_silent_warming(
        self,
        tracking_start_date: Union[str, date],
        eval_date: date,
    ) -> bool:
        """
        Determines whether the student profile is in the initial 7-day silent warming window.

        Returns True if (eval_date - tracking_start_date).days < 7.
        """
        start = self._parse_date(tracking_start_date)
        return (eval_date - start).days < 7

    def is_noise_suppressed(
        self,
        total_graded_points: Optional[float],
        term_active_days: Optional[int],
    ) -> bool:
        """
        Determines whether alert should be suppressed due to early-term noise.

        Suppressed if total_graded_points < 100 AND term_active_days < 21.
        """
        if total_graded_points is not None and term_active_days is not None:
            if total_graded_points < 100 and term_active_days < 21:
                return True
        return False

    def find_baseline_snapshot(
        self,
        history: List[GradeSnapshot],
        eval_date: date,
    ) -> Optional[GradeSnapshot]:
        """
        Finds historical baseline snapshot in target range [eval_date - 10, eval_date - 7].
        Fallback range: [eval_date - 14, eval_date - 7].
        Returns None if no snapshot exists in range.
        """
        if not history:
            return None

        # Filter valid snapshots with parsed dates
        parsed_history = []
        for snap in history:
            try:
                snap_d = self._parse_date(snap.date)
                parsed_history.append((snap_d, snap))
            except ValueError:
                continue

        # Sort by date descending (closest to eval_date first)
        parsed_history.sort(key=lambda x: x[0], reverse=True)

        # 1. Target window: [eval_date - 10, eval_date - 7]
        target_snapshots = [
            snap for snap_d, snap in parsed_history
            if 7 <= (eval_date - snap_d).days <= 10
        ]
        if target_snapshots:
            return target_snapshots[0]

        # 2. Fallback window: [eval_date - 14, eval_date - 7]
        fallback_snapshots = [
            snap for snap_d, snap in parsed_history
            if 7 <= (eval_date - snap_d).days <= 14
        ]
        if fallback_snapshots:
            return fallback_snapshots[0]

        return None

    def evaluate_student_velocity(
        self,
        student_context: StudentVelocityContext,
        eval_date: Optional[date] = None,
    ) -> List[PendingGradeDropAlert]:
        """
        Evaluates grade velocity for all courses in a student's context.

        Args:
            student_context: Student velocity context including tracking start date and courses with history.
            eval_date: Optional evaluation date (defaults to current UTC date).

        Returns:
            List[PendingGradeDropAlert]: List of triggered alerts for courses with delta >= 4.0%.
        """
        if eval_date is None:
            eval_date = datetime.now(timezone.utc).date()

        # Check Silent Warming Protocol
        if self.is_silent_warming(student_context.tracking_start_date, eval_date):
            return []

        alerts: List[PendingGradeDropAlert] = []
        now_iso = datetime.now(timezone.utc).isoformat()

        for course in student_context.courses:
            # Check Noise Suppression
            if self.is_noise_suppressed(course.total_graded_points, course.term_active_days):
                continue

            # Find Baseline Snapshot
            baseline = self.find_baseline_snapshot(course.history, eval_date)
            if not baseline:
                continue

            # Calculate Delta
            prev_percentage = baseline.percentage
            curr_percentage = course.current_percentage
            delta = round(prev_percentage - curr_percentage, 2)

            # Check Trigger Threshold
            if delta >= self.drop_threshold:
                alert = PendingGradeDropAlert(
                    course_id=course.course_id,
                    course_name=course.course_name,
                    prev_percentage=prev_percentage,
                    curr_percentage=curr_percentage,
                    delta=delta,
                    detected_at=now_iso,
                )
                alerts.append(alert)

        return alerts
