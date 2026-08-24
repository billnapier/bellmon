"""
Asymmetric System Authority & 36-Hour Grace Period Evaluation Engine.
"""

from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
from typing import Optional, Tuple

from src.storage.models import TrackedAssignment
from src.engine.models import (
    AssignmentStatus,
    AlertSource,
    CanvasAssignmentInput,
    PowerSchoolAssignmentInput,
    PendingMissingAlert,
)


def is_weekend_blackout(dt: datetime) -> bool:
    """
    Checks if a datetime falls within the weekend blackout window:
    Friday 17:00:00 (5:00 PM) to Monday 08:00:00 (8:00 AM) local time.

    Weekday mapping in Python datetime:
    0 = Monday, 1 = Tuesday, 2 = Wednesday, 3 = Thursday,
    4 = Friday, 5 = Saturday, 6 = Sunday.
    """
    wd = dt.weekday()
    if wd == 4:  # Friday
        return dt.hour >= 17
    if wd == 5:  # Saturday
        return True
    if wd == 6:  # Sunday
        return True
    if wd == 0:  # Monday
        return dt.hour < 8
    return False


class AsymmetricAuthorityEngine:
    """
    Evaluates Canvas and PowerSchool assignment missing states independently
    under the Asymmetric System Authority Model.
    """

    def __init__(
        self,
        grace_period_hours: float = 36.0,
        timezone_str: str = "America/Los_Angeles",
    ):
        self.grace_period_hours = grace_period_hours
        self.timezone_str = timezone_str
        self.tz = ZoneInfo(timezone_str)

    def calculate_weekday_elapsed_hours(
        self, start_dt: datetime, end_dt: datetime
    ) -> float:
        """
        Calculates active weekday hours between start_dt and end_dt,
        excluding Friday 17:00:00 to Monday 08:00:00 blackout hours.
        """
        if end_dt <= start_dt:
            return 0.0

        # Ensure datetime objects are localized to the engine's target timezone
        if start_dt.tzinfo is None:
            start_dt = start_dt.replace(tzinfo=timezone.utc).astimezone(self.tz)
        else:
            start_dt = start_dt.astimezone(self.tz)

        if end_dt.tzinfo is None:
            end_dt = end_dt.replace(tzinfo=timezone.utc).astimezone(self.tz)
        else:
            end_dt = end_dt.astimezone(self.tz)

        total_active_seconds = 0.0
        curr = start_dt
        step = timedelta(minutes=1)

        while curr < end_dt:
            nxt = min(curr + step, end_dt)
            duration = (nxt - curr).total_seconds()
            mid = curr + (nxt - curr) / 2
            if not is_weekend_blackout(mid):
                total_active_seconds += duration
            curr = nxt

        return total_active_seconds / 3600.0

    def evaluate_canvas_assignment(
        self,
        item: CanvasAssignmentInput,
        existing_tracked: Optional[TrackedAssignment],
        now: Optional[datetime] = None,
    ) -> Tuple[TrackedAssignment, Optional[PendingMissingAlert]]:
        """
        Evaluates a Canvas assignment state:
        - Non-digital (on_paper, none) -> SUPPRESSED
        - Digital (online_upload) & missing -> GRACE_PERIOD (36h weekday timer)
        - Exceeded 36h weekday timer -> EXPIRED + CANVAS_GRACE_EXPIRED alert
        - Submitted / not missing -> RESOLVED
        """
        if now is None:
            now = datetime.now(timezone.utc)
        elif now.tzinfo is None:
            now = now.replace(tzinfo=timezone.utc)

        now_iso = now.isoformat()
        sub_types = [st.lower() for st in item.submission_types]

        # Check if assignment is purely non-digital (on_paper or none with no digital option)
        is_digital = any(st in ["online_upload", "discussion_topic", "online_quiz", "external_tool"] for st in sub_types)
        is_non_digital = any(st in ["on_paper", "none"] for st in sub_types) and not is_digital

        if is_non_digital:
            tracked = TrackedAssignment(
                title=item.title,
                course_id=item.course_id,
                due_at=item.due_at,
                submission_type=", ".join(item.submission_types),
                status=AssignmentStatus.SUPPRESSED.value,
                first_detected_missing=None,
                alert_dispatched=False,
            )
            return tracked, None

        # Digital submission evaluation
        if not item.is_missing:
            # Student submitted or item is no longer marked missing
            tracked = TrackedAssignment(
                title=item.title,
                course_id=item.course_id,
                due_at=item.due_at,
                submission_type=", ".join(item.submission_types),
                status=AssignmentStatus.RESOLVED.value,
                first_detected_missing=None,
                alert_dispatched=False,
            )
            return tracked, None

        # Item is missing
        first_detected_iso = (
            existing_tracked.first_detected_missing
            if existing_tracked and existing_tracked.first_detected_missing
            else now_iso
        )

        try:
            first_detected_dt = datetime.fromisoformat(first_detected_iso)
        except ValueError:
            first_detected_dt = now

        elapsed_weekday_hours = self.calculate_weekday_elapsed_hours(
            first_detected_dt, now
        )

        if elapsed_weekday_hours >= self.grace_period_hours:
            # Grace period expired -> Trigger P0 Alert
            already_dispatched = (
                existing_tracked.alert_dispatched
                if existing_tracked and existing_tracked.status == AssignmentStatus.EXPIRED.value
                else False
            )
            tracked = TrackedAssignment(
                title=item.title,
                course_id=item.course_id,
                due_at=item.due_at,
                submission_type=", ".join(item.submission_types),
                status=AssignmentStatus.EXPIRED.value,
                first_detected_missing=first_detected_iso,
                alert_dispatched=True,
            )
            alert = None
            if not already_dispatched:
                alert = PendingMissingAlert(
                    assignment_id=item.assignment_id,
                    title=item.title,
                    course_id=item.course_id,
                    due_at=item.due_at,
                    source=AlertSource.CANVAS_GRACE_EXPIRED,
                    points_possible=None,
                    detected_at=now_iso,
                )
            return tracked, alert

        # Still within 36-hour grace period
        tracked = TrackedAssignment(
            title=item.title,
            course_id=item.course_id,
            due_at=item.due_at,
            submission_type=", ".join(item.submission_types),
            status=AssignmentStatus.GRACE_PERIOD.value,
            first_detected_missing=first_detected_iso,
            alert_dispatched=False,
        )
        return tracked, None

    def evaluate_powerschool_assignment(
        self,
        item: PowerSchoolAssignmentInput,
        existing_tracked: Optional[TrackedAssignment],
        now: Optional[datetime] = None,
    ) -> Tuple[TrackedAssignment, Optional[PendingMissingAlert]]:
        """
        Evaluates a PowerSchool assignment record:
        - Marked isMissing: true OR score: 0 -> CONFIRMED_MISSING + POWERSCHOOL_CONFIRMED alert
        - Otherwise -> RESOLVED
        """
        if now is None:
            now = datetime.now(timezone.utc)
        elif now.tzinfo is None:
            now = now.replace(tzinfo=timezone.utc)

        now_iso = now.isoformat()
        is_confirmed_missing = item.is_missing or (
            item.score is not None and item.score == 0
        )

        if is_confirmed_missing:
            already_dispatched = (
                existing_tracked.alert_dispatched
                if existing_tracked and existing_tracked.status == AssignmentStatus.CONFIRMED_MISSING.value
                else False
            )

            tracked = TrackedAssignment(
                title=item.title,
                course_id=item.course_id,
                due_at=item.due_at or "",
                submission_type="powerschool_gradebook",
                status=AssignmentStatus.CONFIRMED_MISSING.value,
                first_detected_missing=existing_tracked.first_detected_missing if existing_tracked else now_iso,
                alert_dispatched=True,
            )

            alert = None
            if not already_dispatched:
                alert = PendingMissingAlert(
                    assignment_id=item.assignment_id,
                    title=item.title,
                    course_id=item.course_id,
                    due_at=item.due_at,
                    source=AlertSource.POWERSCHOOL_CONFIRMED,
                    points_possible=item.points_possible,
                    detected_at=now_iso,
                )
            return tracked, alert

        # PowerSchool assignment is not missing and has non-zero score
        tracked = TrackedAssignment(
            title=item.title,
            course_id=item.course_id,
            due_at=item.due_at or "",
            submission_type="powerschool_gradebook",
            status=AssignmentStatus.RESOLVED.value,
            first_detected_missing=None,
            alert_dispatched=False,
        )
        return tracked, None
