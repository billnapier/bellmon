"""
Late Submission Sentinel Engine for monitoring Canvas late submission trends.
Calculates late submission frequencies over rolling 7-day windows, applies noise thresholds,
evaluates warning alert triggers, and manages 7-day cooldown deduplication.
"""

from datetime import datetime, timezone, timedelta
from typing import List, Optional, Tuple, Dict, Any, Union
from src.storage.models import LateSubmissionRecord, DispatchedAlertRecord
from src.engine.models import LateSubmissionPatternAlert


def parse_iso(ts_str: Optional[str]) -> Optional[datetime]:
    """Helper to parse ISO format timestamp strings to UTC-aware datetime."""
    if not ts_str:
        return None
    try:
        dt = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except (ValueError, TypeError):
        return None


class LateSubmissionSentinel:
    """Sentinel engine for late submission frequency evaluation and pattern warning alert generation."""

    def evaluate_late_submissions(
        self,
        student_id: str,
        records: List[LateSubmissionRecord],
        now: Optional[datetime] = None,
        min_minutes_late: int = 5,
        frequency_threshold: int = 3,
        dispatched_alerts: Optional[List[Union[DispatchedAlertRecord, Dict[str, Any]]]] = None,
    ) -> Tuple[Optional[LateSubmissionPatternAlert], List[LateSubmissionRecord]]:
        """
        Evaluate late submission records within a rolling 7-day window.

        Args:
            student_id: Student identifier.
            records: List of harvested LateSubmissionRecord items.
            now: Reference datetime (defaults to UTC now if None).
            min_minutes_late: Noise threshold in minutes (default 5).
            frequency_threshold: Number of late submissions required to trigger P1 alert (default 3).
            dispatched_alerts: History of dispatched alerts for deduplication/cooldown check.

        Returns:
            Tuple of (Optional[LateSubmissionPatternAlert], List[LateSubmissionRecord])
            where the list contains all qualifying late submission records in the 7-day window.
        """
        if now is None:
            now = datetime.now(timezone.utc)
        elif now.tzinfo is None:
            now = now.replace(tzinfo=timezone.utc)

        window_start = now - timedelta(days=7)

        qualifying_records: List[LateSubmissionRecord] = []

        for record in records:
            if not record.is_late:
                continue

            if record.minutes_late < min_minutes_late:
                continue

            ts_str = record.submitted_at or record.detected_at
            rec_dt = parse_iso(ts_str)

            if rec_dt is None:
                continue

            if window_start <= rec_dt <= now:
                qualifying_records.append(record)

        qualifying_count = len(qualifying_records)

        # Check threshold trigger
        if qualifying_count < frequency_threshold:
            return None, qualifying_records

        # Check 7-day cooldown against dispatched alerts
        if dispatched_alerts:
            cooldown_start = now - timedelta(days=7)
            for alert in dispatched_alerts:
                alert_type = (
                    alert.alert_type
                    if isinstance(alert, DispatchedAlertRecord)
                    else alert.get("alert_type")
                )
                dispatched_at_str = (
                    alert.dispatched_at
                    if isinstance(alert, DispatchedAlertRecord)
                    else alert.get("dispatched_at")
                )

                if alert_type == "LATE_SUBMISSION_FREQUENCY_WARNING":
                    dispatched_dt = parse_iso(dispatched_at_str)
                    if dispatched_dt and cooldown_start <= dispatched_dt <= now:
                        # Alert is suppressed due to active 7-day cooldown
                        return None, qualifying_records

        # Trigger P1 pattern alert
        alert = LateSubmissionPatternAlert(
            student_id=student_id,
            count_in_window=qualifying_count,
            qualifying_records=qualifying_records,
            detected_at=now.isoformat(),
            severity="P1_WARNING",
        )

        return alert, qualifying_records
