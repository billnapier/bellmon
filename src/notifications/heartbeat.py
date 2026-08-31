"""
Daily Heartbeat & System Activity Briefing Generator.
"""

import logging
from datetime import datetime, timezone
from typing import Optional, List, Any

from src.notifications.models import (
    HeartbeatPayload,
    GraceWatchlistItem,
    PortalIngestionRecord,
    DailyAttendanceSummary,
    AttendancePeriodRecord,
    EmailPayload,
    DispatchResult,
)
from src.notifications.renderer import NotificationRenderer
from src.notifications.router import NotificationRouter
from src.storage.firestore import FirestoreStateEngine
from src.engine.authority import AsymmetricAuthorityEngine
from src.storage.models import HeartbeatDispatchRecord

logger = logging.getLogger("bellmon.notifications.heartbeat")


class HeartbeatBriefingGenerator:
    """Collects daily system activity & telemetry and dispatches daily heartbeat briefings."""

    def __init__(
        self,
        db_client: Optional[Any] = None,
        router: Optional[NotificationRouter] = None,
        renderer: Optional[NotificationRenderer] = None,
        state_engine: Optional[FirestoreStateEngine] = None,
        authority_engine: Optional[AsymmetricAuthorityEngine] = None,
    ):
        """
        Initializes HeartbeatBriefingGenerator.

        Args:
            db_client: Optional Firestore client instance.
            router: Optional NotificationRouter instance.
            renderer: Optional NotificationRenderer instance.
            state_engine: Optional FirestoreStateEngine instance.
            authority_engine: Optional AsymmetricAuthorityEngine instance.
        """
        self.db = db_client
        self.router = router or NotificationRouter()
        self.renderer = renderer or NotificationRenderer()
        self.state_engine = state_engine or FirestoreStateEngine(db_client=self.db)
        self.authority = authority_engine or AsymmetricAuthorityEngine()

    def collect_telemetry(self, student_id: str, date: str) -> HeartbeatPayload:
        """
        Gathers system health, grace watchlist, attendance, and alert standing telemetry.

        Args:
            student_id: ID of the student.
            date: YYYY-MM-DD date string.

        Returns:
            HeartbeatPayload containing compiled daily telemetry.
        """
        # 1. Ingestion Health
        canvas_status = "OPERATIONAL"
        powerschool_status = "OPERATIONAL"
        ingestion_records = [
            PortalIngestionRecord(portal_name="Canvas API", status=canvas_status),
            PortalIngestionRecord(portal_name="PowerSchool Portal", status=powerschool_status),
        ]

        if self.db:
            try:
                ing_doc_ref = self.db.collection("ingestion_status").document(date)
                ing_doc = ing_doc_ref.get()
                exists = getattr(ing_doc, "exists", False)
                if callable(exists):
                    exists = exists()
                if not exists:
                    ing_doc_ref = self.db.collection("ingestion_status").document(f"{student_id}_{date}")
                    ing_doc = ing_doc_ref.get()
                    exists = getattr(ing_doc, "exists", False)
                    if callable(exists):
                        exists = exists()
                
                if exists and hasattr(ing_doc, "to_dict"):
                    data = ing_doc.to_dict()
                    if isinstance(data, dict):
                        c_status = data.get("canvas_status")
                        if isinstance(c_status, str):
                            canvas_status = c_status
                        p_status = data.get("powerschool_status")
                        if isinstance(p_status, str):
                            powerschool_status = p_status
                        ingestion_records = [
                            PortalIngestionRecord(portal_name="Canvas API", status=canvas_status),
                            PortalIngestionRecord(portal_name="PowerSchool Portal", status=powerschool_status),
                        ]
            except Exception as e:
                logger.warning(f"Failed to fetch ingestion status from Firestore: {e}")

        # 2. Grace Period Watchlist
        grace_watchlist: List[GraceWatchlistItem] = []
        try:
            late_items = self.state_engine.get_late_submissions(student_id)
            now_dt = datetime.now(timezone.utc)

            for item in late_items:
                status = getattr(item, "status", None) or (item.get("status") if isinstance(item, dict) else None)
                if status == "GRACE_PERIOD":
                    title = getattr(item, "title", None) or (item.get("title") if isinstance(item, dict) else "Assignment")
                    course_id = getattr(item, "course_id", None) or (item.get("course_id") if isinstance(item, dict) else "Course")
                    course_name = getattr(item, "course_name", None) or (item.get("course_name") if isinstance(item, dict) else course_id)
                    due_at = getattr(item, "due_at", None) or (item.get("due_at") if isinstance(item, dict) else "N/A")
                    first_detected = getattr(item, "first_detected_missing", None) or (item.get("first_detected_missing") if isinstance(item, dict) else None)

                    hours_remaining = 36.0
                    if first_detected:
                        try:
                            start_dt = datetime.fromisoformat(first_detected)
                            elapsed = self.authority.calculate_weekday_elapsed_hours(start_dt, now_dt)
                            hours_remaining = max(0.0, round(36.0 - elapsed, 1))
                        except Exception as e:
                            logger.warning(f"Error calculating grace period remaining hours: {e}")

                    grace_watchlist.append(
                        GraceWatchlistItem(
                            assignment_id=getattr(item, "assignment_id", "") or (item.get("assignment_id", "") if isinstance(item, dict) else ""),
                            title=title,
                            course_id=course_id,
                            course_name=course_name,
                            due_at=due_at,
                            first_detected_missing=first_detected or now_dt.isoformat(),
                            hours_remaining=hours_remaining,
                        )
                    )
        except Exception as e:
            logger.warning(f"Error fetching grace period items: {e}")

        # 3. Daily Attendance Summary
        attendance_summary = DailyAttendanceSummary(
            date=date,
            total_anomalies=0,
            records=[],
        )
        if self.db:
            try:
                att_doc = self.db.collection("attendance_records").document(f"{student_id}_{date}").get()
                exists = getattr(att_doc, "exists", False)
                if callable(exists):
                    exists = exists()
                if exists and hasattr(att_doc, "to_dict"):
                    att_data = att_doc.to_dict()
                    if isinstance(att_data, dict):
                        records_data = att_data.get("records", [])
                        if isinstance(records_data, list):
                            records_objs = [
                                AttendancePeriodRecord(
                                    period=r.get("period", 1) if isinstance(r, dict) else 1,
                                    course_name=r.get("course_name", "") if isinstance(r, dict) else "",
                                    status=r.get("status", "PRESENT") if isinstance(r, dict) else "PRESENT",
                                    description=r.get("description", "") if isinstance(r, dict) else "",
                                )
                                for r in records_data if isinstance(r, dict)
                            ]
                            attendance_summary = DailyAttendanceSummary(
                                date=date,
                                total_anomalies=att_data.get("total_anomalies", 0) if isinstance(att_data.get("total_anomalies"), int) else 0,
                                records=records_objs,
                            )
            except Exception as e:
                logger.warning(f"Failed to fetch attendance summary from Firestore: {e}")


        # 4. Critical Alerts Standing
        dispatched_alerts = []
        try:
            dispatched_alerts = self.state_engine.get_dispatched_alerts(student_id)
            # Filter alerts for specified date if timestamp available
            dispatched_alerts = [
                a for a in dispatched_alerts
                if str(getattr(a, "dispatched_at", "")).startswith(date) or str(a.get("dispatched_at", "")).startswith(date)
            ] if isinstance(dispatched_alerts, list) else []
        except Exception as e:
            logger.warning(f"Failed to fetch dispatched alerts: {e}")

        alerts_count = len(dispatched_alerts)
        zero_alert_confirmed = (alerts_count == 0)

        return HeartbeatPayload(
            student_id=student_id,
            student_name=student_id,
            date=date,
            sync_timestamp=datetime.now(timezone.utc).isoformat(),
            canvas_status=canvas_status,
            powerschool_status=powerschool_status,
            ingestion_statuses=ingestion_records,
            grace_watchlist=grace_watchlist,
            attendance_summary=attendance_summary,
            alerts_dispatched_today=alerts_count,
            zero_alert_confirmed=zero_alert_confirmed,
        )

    def generate_and_dispatch(
        self,
        student_id: str,
        recipient_email: str,
        student_name: str,
        date: str,
    ) -> Optional[DispatchResult]:
        """
        Generates and dispatches daily heartbeat email with idempotency protection.

        Args:
            student_id: ID of the student.
            recipient_email: Destination email address.
            student_name: Display name of the student.
            date: YYYY-MM-DD date string.

        Returns:
            DispatchResult tracking dispatch outcome.
        """
        doc_id = f"{student_id}_{date}"

        # 1. Idempotency Check
        if self.db:
            try:
                record_doc = self.db.collection("heartbeat_briefings").document(doc_id).get()
                if record_doc.exists:
                    data = record_doc.to_dict() or {}
                    if data.get("status") == "SUCCESS":
                        logger.info(f"Heartbeat briefing already dispatched for {doc_id}. Skipping.")
                        return DispatchResult(
                            success=True,
                            message_id=data.get("message_id", "already_sent_idempotent"),
                            recipient=recipient_email,
                            timestamp=data.get("dispatched_at", datetime.now(timezone.utc).isoformat()),
                            dry_run=data.get("dry_run", False),
                        )
            except Exception as e:
                logger.warning(f"Idempotency check failed: {e}")

        # 2. Collect Telemetry
        payload = self.collect_telemetry(student_id, date)
        payload.student_name = student_name

        # 3. Render Email
        html_body, text_fallback = self.renderer.compile_heartbeat_email(payload)
        subject = f"[BELLMON DAILY HEARTBEAT] {student_name}: System Activity Briefing ({date})"

        email_payload = EmailPayload(
            recipient_email=recipient_email,
            student_name=student_name,
            subject=subject,
            html_body=html_body,
            text_fallback=text_fallback,
        )

        # 4. Dispatch Email
        logger.info(f"Dispatching daily heartbeat email for {student_name} ({student_id}) on {date}")
        dispatch_result = self.router.client.send_email(email_payload)

        # 5. Record Dispatch Outcome
        if dispatch_result and dispatch_result.success and self.db:
            try:
                record = HeartbeatDispatchRecord(
                    student_id=student_id,
                    student_name=student_name,
                    date=date,
                    recipient_email=recipient_email,
                    dispatched_at=dispatch_result.timestamp or datetime.now(timezone.utc).isoformat(),
                    message_id=dispatch_result.message_id or "",
                    status="SUCCESS",
                    dry_run=dispatch_result.dry_run,
                )
                self.db.collection("heartbeat_briefings").document(doc_id).set(record.to_dict())
            except Exception as e:
                logger.error(f"Failed to record heartbeat dispatch record in Firestore: {e}")

        return dispatch_result
