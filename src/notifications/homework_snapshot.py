"""
Daily Evening Homework & Deadline Snapshot Generator.
"""

import logging
from datetime import datetime, timezone, timedelta
from typing import Optional, List, Any, Dict

from src.notifications.models import (
    HomeworkSnapshotPayload,
    UpcomingDeadlineItem,
    GracePeriodSnapshotItem,
    RecentlyCompletedItem,
    EmailPayload,
    DispatchResult,
)
from src.notifications.renderer import NotificationRenderer
from src.notifications.router import NotificationRouter
from src.storage.firestore import FirestoreStateEngine
from src.engine.authority import AsymmetricAuthorityEngine

logger = logging.getLogger("bellmon.notifications.homework_snapshot")


class HomeworkSnapshotGenerator:
    """Collects daily evening homework & deadline telemetry and dispatches snapshot emails."""

    def __init__(
        self,
        db_client: Optional[Any] = None,
        router: Optional[NotificationRouter] = None,
        renderer: Optional[NotificationRenderer] = None,
        state_engine: Optional[FirestoreStateEngine] = None,
        authority_engine: Optional[AsymmetricAuthorityEngine] = None,
    ):
        """
        Initializes HomeworkSnapshotGenerator.

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

    def _fetch_collection_data(self, collection_name: str, student_id: str) -> List[Dict[str, Any]]:
        items: List[Dict[str, Any]] = []
        if not self.db:
            return items

        if hasattr(self.db, "query_collection") and callable(getattr(self.db, "query_collection")):
            try:
                res = self.db.query_collection(collection_name, student_id=student_id)
                if isinstance(res, list):
                    for item in res:
                        if isinstance(item, dict):
                            items.append(item)
                        elif hasattr(item, "to_dict"):
                            items.append(item.to_dict())
                    return items
            except Exception as e:
                logger.debug(f"query_collection failed for {collection_name}: {e}")

        if hasattr(self.db, "collection") and callable(getattr(self.db, "collection")):
            try:
                col_ref = self.db.collection(collection_name)
                docs = []
                if hasattr(col_ref, "where"):
                    try:
                        docs = col_ref.where("student_id", "==", student_id).stream()
                    except Exception:
                        docs = col_ref.stream()
                else:
                    docs = col_ref.stream()

                for d in docs:
                    d_dict = d.to_dict() if hasattr(d, "to_dict") else {}
                    if isinstance(d_dict, dict):
                        items.append(d_dict)
                return items
            except Exception as e:
                logger.debug(f"Firestore stream failed for {collection_name}: {e}")

        return items

    def collect_snapshot(
        self,
        student_id: str,
        student_name: str = "Student",
        snapshot_time: Optional[datetime] = None,
    ) -> HomeworkSnapshotPayload:
        """
        Gathers upcoming deadlines (24-48h window), active grace period items, and recently completed work.

        Args:
            student_id: ID of the student.
            student_name: Display name of the student.
            snapshot_time: Optional snapshot timestamp (defaults to UTC now).

        Returns:
            HomeworkSnapshotPayload containing compiled snapshot items.
        """
        now_dt = snapshot_time or datetime.now(timezone.utc)
        if now_dt.tzinfo is None:
            now_dt = now_dt.replace(tzinfo=timezone.utc)

        window_end_dt = now_dt + timedelta(hours=48)
        past_24h_dt = now_dt - timedelta(hours=24)

        upcoming_deadlines: List[UpcomingDeadlineItem] = []
        grace_period_items: List[GracePeriodSnapshotItem] = []
        recently_completed: List[RecentlyCompletedItem] = []

        # 1. Fetch raw assignments & late submissions from Firestore / State Engine
        assignments_data = self._fetch_collection_data("assignments", student_id)

        # 2. Process Grace Period Items from db or State Engine
        grace_data = self._fetch_collection_data("grace_period_items", student_id)
        try:
            late_items = self.state_engine.get_late_submissions(student_id)
            for item in late_items:
                if isinstance(item, dict):
                    grace_data.append(item)
                else:
                    item_dict = item.model_dump(mode="json") if hasattr(item, "model_dump") else {}
                    grace_data.append(item_dict)
        except Exception as e:
            logger.debug(f"State engine get_late_submissions check: {e}")

        seen_grace_ids = set()
        for item in grace_data:
            status = item.get("status")
            if status == "GRACE_PERIOD":
                assign_id = str(item.get("assignment_id") or item.get("id") or "")
                if assign_id in seen_grace_ids:
                    continue
                seen_grace_ids.add(assign_id)

                title = str(item.get("title") or item.get("name") or "Assignment")
                course = str(item.get("course_name") or item.get("course") or item.get("course_id") or "Course")
                due_at = str(item.get("original_due_at") or item.get("due_at") or "")
                first_detected = item.get("first_detected_missing")
                grace_expires = item.get("grace_expires_at")
                submission_url = item.get("submission_url")
                portal = str(item.get("portal") or "Canvas")

                hours_remaining = 36.0
                if grace_expires:
                    try:
                        exp_dt = datetime.fromisoformat(str(grace_expires))
                        if exp_dt.tzinfo is None:
                            exp_dt = exp_dt.replace(tzinfo=timezone.utc)
                        hours_remaining = max(0.0, round((exp_dt - now_dt).total_seconds() / 3600.0, 1))
                    except Exception as e:
                        logger.warning(f"Error parsing grace_expires_at: {e}")
                elif first_detected:
                    try:
                        start_dt = datetime.fromisoformat(str(first_detected))
                        if start_dt.tzinfo is None:
                            start_dt = start_dt.replace(tzinfo=timezone.utc)
                        elapsed = self.authority.calculate_weekday_elapsed_hours(start_dt, now_dt)
                        hours_remaining = max(0.0, round(36.0 - elapsed, 1))
                    except Exception as e:
                        logger.warning(f"Error calculating grace period remaining hours: {e}")

                grace_period_items.append(
                    GracePeriodSnapshotItem(
                        assignment_id=assign_id,
                        title=title,
                        course=course,
                        original_due_at=due_at,
                        hours_remaining=hours_remaining,
                        portal=portal,
                        submission_url=submission_url,
                    )
                )

        # 3. Categorize Assignments (Upcoming & Recently Completed)
        for assign in assignments_data:
            assign_id = str(assign.get("assignment_id") or assign.get("id") or "")
            title = str(assign.get("title") or assign.get("name") or "Assignment")
            course = str(assign.get("course_name") or assign.get("course") or "General")
            due_at_raw = assign.get("due_at")
            submitted_raw = assign.get("submitted", False)
            submitted_at_raw = assign.get("submitted_at")
            portal = str(assign.get("portal") or "Canvas")
            submission_url = assign.get("submission_url")

            # Asymmetric Authority Check: Canvas submission overrides missing status
            canvas_status = str(assign.get("canvas_status") or "").lower()
            canvas_submitted = assign.get("canvas_submitted", False) or canvas_status == "submitted"
            is_submitted = bool(submitted_raw or canvas_submitted)

            # Check due_at window
            due_dt = None
            if due_at_raw:
                try:
                    due_dt = datetime.fromisoformat(str(due_at_raw))
                    if due_dt.tzinfo is None:
                        due_dt = due_dt.replace(tzinfo=timezone.utc)
                except Exception:
                    due_dt = None

            if due_dt and now_dt <= due_dt <= window_end_dt:
                upcoming_deadlines.append(
                    UpcomingDeadlineItem(
                        assignment_id=assign_id,
                        title=title,
                        course=course,
                        due_at=due_dt.isoformat(),
                        portal=portal,
                        submitted=is_submitted,
                        submission_url=submission_url,
                    )
                )

            # Check recently completed in past 24h
            submitted_dt = None
            if submitted_at_raw:
                try:
                    submitted_dt = datetime.fromisoformat(str(submitted_at_raw))
                    if submitted_dt.tzinfo is None:
                        submitted_dt = submitted_dt.replace(tzinfo=timezone.utc)
                except Exception:
                    submitted_dt = None

            if is_submitted and submitted_dt and past_24h_dt <= submitted_dt <= now_dt:
                recently_completed.append(
                    RecentlyCompletedItem(
                        assignment_id=assign_id,
                        title=title,
                        course=course,
                        submitted_at=submitted_dt.isoformat(),
                        portal=portal,
                    )
                )

        # Sort upcoming chronologically by due_at
        upcoming_deadlines.sort(key=lambda x: x.due_at)

        return HomeworkSnapshotPayload(
            generated_at=now_dt.isoformat(),
            student_id=student_id,
            student_name=student_name,
            upcoming_deadlines=upcoming_deadlines,
            grace_period_items=grace_period_items,
            recently_completed=recently_completed,
        )

    def collect_snapshot_data(
        self,
        student_id: str,
        snapshot_time: Optional[datetime] = None,
        student_name: str = "Student",
    ) -> HomeworkSnapshotPayload:
        """Alias for collect_snapshot."""
        return self.collect_snapshot(
            student_id=student_id,
            student_name=student_name,
            snapshot_time=snapshot_time,
        )

    def generate_and_dispatch(
        self,
        student_id: str,
        recipient_email: str,
        student_name: str,
        snapshot_time: Optional[datetime] = None,
    ) -> Optional[DispatchResult]:
        """
        Generates and dispatches daily homework snapshot email with idempotency protection.

        Args:
            student_id: ID of the student.
            recipient_email: Destination email address.
            student_name: Display name of the student.
            snapshot_time: Optional snapshot timestamp.

        Returns:
            DispatchResult tracking dispatch outcome.
        """
        now_dt = snapshot_time or datetime.now(timezone.utc)
        date_str = now_dt.strftime("%Y-%m-%d")
        doc_id = f"{student_id}_{date_str}"

        # 1. Idempotency Check
        if self.db:
            try:
                record_data = None
                if hasattr(self.db, "get_document") and callable(getattr(self.db, "get_document")):
                    record_data = self.db.get_document("homework_snapshots", doc_id)
                elif hasattr(self.db, "collection") and callable(getattr(self.db, "collection")):
                    record_doc = self.db.collection("homework_snapshots").document(doc_id).get()
                    exists = getattr(record_doc, "exists", False)
                    if callable(exists):
                        exists = exists()
                    if exists:
                        record_data = record_doc.to_dict() or {}

                if record_data:
                    logger.info(f"Homework snapshot already dispatched for {doc_id}. Skipping.")
                    return DispatchResult(
                        success=False,
                        message_id=record_data.get("message_id", "already_sent_idempotent"),
                        recipient=recipient_email,
                        timestamp=record_data.get("dispatched_at") or record_data.get("sent_at", now_dt.isoformat()),
                        error_message="Snapshot already sent today for this student.",
                        dry_run=record_data.get("dry_run", False),
                    )
            except Exception as e:
                logger.warning(f"Homework snapshot idempotency check failed: {e}")

        # 2. Collect Snapshot Payload
        payload = self.collect_snapshot(student_id=student_id, student_name=student_name, snapshot_time=now_dt)

        # 3. Render Email
        html_body, text_fallback = self.renderer.compile_homework_snapshot_email(payload)
        subject = f"[BELLMON HOMEWORK SNAPSHOT] {student_name}: Evening Homework & Deadline Snapshot ({date_str})"

        email_payload = EmailPayload(
            recipient_email=recipient_email,
            student_name=student_name,
            subject=subject,
            html_body=html_body,
            text_fallback=text_fallback,
        )

        # 4. Dispatch Email
        logger.info(f"Dispatching daily homework snapshot for {student_name} ({student_id}) on {date_str}")
        dispatch_result = None
        if hasattr(self.router, "dispatch") and callable(getattr(self.router, "dispatch")):
            dispatch_result = self.router.dispatch(email_payload)
        elif hasattr(self.router, "client") and hasattr(self.router.client, "send_email"):
            dispatch_result = self.router.client.send_email(email_payload)

        # 5. Record Dispatch Outcome
        if dispatch_result and dispatch_result.success and self.db:
            try:
                record_data = {
                    "student_id": student_id,
                    "student_name": student_name,
                    "date": date_str,
                    "recipient_email": recipient_email,
                    "dispatched_at": dispatch_result.timestamp or now_dt.isoformat(),
                    "message_id": dispatch_result.message_id or "",
                    "status": "SENT",
                    "upcoming_count": len(payload.upcoming_deadlines),
                    "grace_count": len(payload.grace_period_items),
                    "completed_count": len(payload.recently_completed),
                    "dry_run": dispatch_result.dry_run,
                }
                if hasattr(self.db, "save_document") and callable(getattr(self.db, "save_document")):
                    self.db.save_document("homework_snapshots", doc_id, record_data)
                elif hasattr(self.db, "collection") and callable(getattr(self.db, "collection")):
                    self.db.collection("homework_snapshots").document(doc_id).set(record_data)
            except Exception as e:
                logger.error(f"Failed to record homework snapshot dispatch record in Firestore: {e}")

        return dispatch_result
