from typing import Tuple
from src.storage.models import AttendanceEvent


class AttendanceEvaluator:
    UNEXCUSED_CODES = {"A", "T", "U", "CUT"}

    def evaluate(self, event: AttendanceEvent) -> Tuple[bool, str, str]:
        """
        Evaluates daily attendance records for unexcused anomalies.
        Returns: (should_alert: bool, title: str, message: str)
        """
        if event.code in self.UNEXCUSED_CODES or event.is_unexcused:
            title = f"⚠️ Attendance Anomaly: Period {event.period} ({event.code})"
            msg = f"Student logged attendance code '{event.code}' ({event.description}) on {event.date} for Period {event.period}."
            return True, title, msg

        return False, "", ""
