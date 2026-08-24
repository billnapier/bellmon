"""
Notification Router for Aggregated P0 Alert Dispatching.
"""

import os
import logging
from typing import List, Any, Optional

from src.notifications.models import EmailPayload, DispatchResult
from src.notifications.renderer import NotificationRenderer
from src.notifications.sendgrid import SendGridClient

logger = logging.getLogger("bellmon.notifications.router")


class NotificationRouter:
    """Aggregates pending P0 alerts, renders responsive bodies, and orchestrates email dispatch."""

    def __init__(
        self,
        sendgrid_client: Optional[SendGridClient] = None,
        renderer: Optional[NotificationRenderer] = None,
        dry_run: Optional[bool] = None,
    ):
        """
        Initializes NotificationRouter.

        Args:
            sendgrid_client: Custom or default SendGridClient.
            renderer: Custom or default NotificationRenderer.
            dry_run: Forced dry-run flag.
        """
        self.client = sendgrid_client or SendGridClient(dry_run=dry_run)
        self.renderer = renderer or NotificationRenderer()

    def dispatch_alerts(
        self,
        recipient_email: str,
        student_name: str,
        missing_work: List[Any] = None,
        grade_drops: List[Any] = None,
        attendance_anomalies: List[Any] = None,
    ) -> Optional[DispatchResult]:
        """
        Aggregates pending P0 alerts into a single email dispatch per student.

        Args:
            recipient_email: Destination email address.
            student_name: Name or ID of the student.
            missing_work: Confirmed missing work alerts.
            grade_drops: Grade velocity drop alerts.
            attendance_anomalies: Attendance anomaly alerts.

        Returns:
            DispatchResult tracking success status, or None if no alerts were pending.
        """
        missing_work = missing_work or []
        grade_drops = grade_drops or []
        attendance_anomalies = attendance_anomalies or []

        total_alerts = len(missing_work) + len(grade_drops) + len(attendance_anomalies)

        if total_alerts == 0:
            logger.info("Zero P0 alerts pending; no email sent.")
            return None

        # Build subject line based on highest severity / count
        categories = []
        if missing_work:
            categories.append(f"{len(missing_work)} Missing Work")
        if grade_drops:
            categories.append(f"{len(grade_drops)} Grade Drop")
        if attendance_anomalies:
            categories.append(f"{len(attendance_anomalies)} Attendance Anomaly")

        category_summary = ", ".join(categories)
        subject = f"[BELLMON P0 ALERT] {student_name}: {category_summary}"

        # Render responsive HTML and text bodies
        html_body, text_fallback = self.renderer.compile_p0_email(
            student_name=student_name,
            missing_work=missing_work,
            grade_drops=grade_drops,
            attendance_anomalies=attendance_anomalies,
        )

        payload = EmailPayload(
            recipient_email=recipient_email,
            student_name=student_name,
            subject=subject,
            html_body=html_body,
            text_fallback=text_fallback,
            missing_work_alerts=missing_work,
            grade_drop_alerts=grade_drops,
            attendance_alerts=attendance_anomalies,
        )

        logger.info(f"Triggering email dispatch for {student_name} ({total_alerts} P0 alerts) to {recipient_email}")
        return self.client.send_email(payload)
