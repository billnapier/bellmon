"""
Attendance Sentinel Engine for Phase 1.4 Period Attendance Anomaly Detection.
"""

from datetime import datetime, timezone
from typing import List, Optional, Tuple, Dict
from src.engine.models import (
    AttendanceCodeSeverity,
    AttendanceRecordInput,
    AttendanceEvent,
    PendingAttendanceAlert,
)


class AttendanceSentinel:
    """Evaluates period-level attendance records harvested from PowerSchool

    against classification rules and deduplication state.
    """

    P0_CODES = {"A", "CUT"}
    P1_CODES = {"T", "U"}
    IGNORED_CODES = {"P", "E", "EX", "ACT"}

    @classmethod
    def classify_code(cls, code: str) -> AttendanceCodeSeverity:
        """Categorize an attendance code into P0_URGENT, P1_DIGEST, or IGNORED."""
        normalized_code = code.strip().upper() if code else ""
        if normalized_code in cls.P0_CODES:
            return AttendanceCodeSeverity.P0_URGENT
        elif normalized_code in cls.P1_CODES:
            return AttendanceCodeSeverity.P1_DIGEST
        else:
            return AttendanceCodeSeverity.IGNORED

    def evaluate_student_attendance(
        self,
        student_id: str,
        records: List[AttendanceRecordInput],
        existing_events: List[AttendanceEvent],
        now: Optional[datetime] = None,
    ) -> Tuple[List[PendingAttendanceAlert], List[AttendanceEvent]]:
        """Evaluates raw attendance records for a student against existing ledger history.

        Args:
            student_id: Unique identifier for the student.
            records: List of raw harvested AttendanceRecordInput entries.
            existing_events: List of previously stored AttendanceEvent records.
            now: Optional datetime override for testing.

        Returns:
            Tuple of:
            - List[PendingAttendanceAlert]: Pending P0 urgent alert payloads.
            - List[AttendanceEvent]: Complete updated list of AttendanceEvents for persistence.
        """
        eval_time = now or datetime.now(timezone.utc)
        timestamp_iso = eval_time.isoformat()

        updated_events_map: Dict[Tuple[str, str, str], AttendanceEvent] = {}
        for event in existing_events:
            key = (str(event.date), str(event.period), str(event.course_name))
            updated_events_map[key] = event.model_copy()

        alerts: List[PendingAttendanceAlert] = []

        for rec in records:
            key = (str(rec.date), str(rec.period), str(rec.course_name))
            norm_code = rec.code.strip().upper() if rec.code else ""
            severity = self.classify_code(norm_code)
            existing = updated_events_map.get(key)

            default_desc = rec.description
            if not default_desc:
                if norm_code == "A":
                    default_desc = "Unexcused Absence"
                elif norm_code == "CUT":
                    default_desc = "Class Cut"
                elif norm_code == "T":
                    default_desc = "Tardy"
                elif norm_code == "U":
                    default_desc = "Unverified Attendance"
                elif norm_code in ("E", "EX"):
                    default_desc = "Excused Absence"
                elif norm_code == "P":
                    default_desc = "Present"
                elif norm_code == "ACT":
                    default_desc = "School Activity"
                else:
                    default_desc = norm_code

            if severity == AttendanceCodeSeverity.IGNORED:
                if existing:
                    existing.code = rec.code
                    existing.severity = AttendanceCodeSeverity.IGNORED
                    existing.description = default_desc
            elif severity == AttendanceCodeSeverity.P0_URGENT:
                if existing:
                    if existing.notified:
                        # Already notified, update attributes if changed, but suppress new alert
                        existing.code = rec.code
                        existing.severity = AttendanceCodeSeverity.P0_URGENT
                        existing.description = default_desc
                    else:
                        existing.code = rec.code
                        existing.severity = AttendanceCodeSeverity.P0_URGENT
                        existing.description = default_desc
                        existing.notified = True
                        alerts.append(
                            PendingAttendanceAlert(
                                student_id=student_id,
                                date=rec.date,
                                period=rec.period,
                                course_name=rec.course_name,
                                code=rec.code,
                                description=default_desc,
                                severity=AttendanceCodeSeverity.P0_URGENT,
                                detected_at=timestamp_iso,
                            )
                        )
                else:
                    new_event = AttendanceEvent(
                        date=rec.date,
                        period=rec.period,
                        course_name=rec.course_name,
                        code=rec.code,
                        description=default_desc,
                        severity=AttendanceCodeSeverity.P0_URGENT,
                        notified=True,
                        detected_at=timestamp_iso,
                    )
                    updated_events_map[key] = new_event
                    alerts.append(
                        PendingAttendanceAlert(
                            student_id=student_id,
                            date=rec.date,
                            period=rec.period,
                            course_name=rec.course_name,
                            code=rec.code,
                            description=default_desc,
                            severity=AttendanceCodeSeverity.P0_URGENT,
                            detected_at=timestamp_iso,
                        )
                    )
            elif severity == AttendanceCodeSeverity.P1_DIGEST:
                if existing:
                    existing.code = rec.code
                    existing.severity = AttendanceCodeSeverity.P1_DIGEST
                    existing.description = default_desc
                else:
                    new_event = AttendanceEvent(
                        date=rec.date,
                        period=rec.period,
                        course_name=rec.course_name,
                        code=rec.code,
                        description=default_desc,
                        severity=AttendanceCodeSeverity.P1_DIGEST,
                        notified=False,
                        detected_at=timestamp_iso,
                    )
                    updated_events_map[key] = new_event

        return alerts, list(updated_events_map.values())
