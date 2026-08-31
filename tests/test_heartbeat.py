"""Unit tests for Daily Heartbeat & System Activity Briefing (Spec 013)."""

from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest

from src.notifications.models import (
    HeartbeatPayload,
    GraceWatchlistItem,
    PortalIngestionRecord,
    DailyAttendanceSummary,
    AttendancePeriodRecord,
)
from src.notifications.renderer import NotificationRenderer
from src.notifications.heartbeat import HeartbeatBriefingGenerator
from src.notifications.router import NotificationRouter
from src.storage.models import TrackedAssignment
from src.engine.models import AssignmentStatus


def test_heartbeat_payload_defaults():
    payload = HeartbeatPayload(
        student_id="student_123",
        student_name="Jane Doe",
        date="2026-08-31",
    )
    assert payload.student_id == "student_123"
    assert payload.student_name == "Jane Doe"
    assert payload.date == "2026-08-31"
    assert payload.canvas_status == "OPERATIONAL"
    assert payload.powerschool_status == "OPERATIONAL"
    assert payload.alerts_dispatched_today == 0
    assert payload.zero_alert_confirmed is True
    assert payload.grace_watchlist == []


def test_heartbeat_renderer_with_grace_items_and_attendance():
    payload = HeartbeatPayload(
        student_id="student_123",
        student_name="Jane Doe",
        date="2026-08-31",
        sync_timestamp="2026-08-31T17:00:00Z",
        canvas_status="OPERATIONAL",
        powerschool_status="DEGRADED",
        ingestion_statuses=[
            PortalIngestionRecord(portal_name="Canvas API", status="OPERATIONAL"),
            PortalIngestionRecord(portal_name="PowerSchool Portal", status="DEGRADED"),
        ],
        grace_watchlist=[
            GraceWatchlistItem(
                assignment_id="a101",
                title="Physics Lab Report",
                course_id="c201",
                course_name="AP Physics",
                due_at="2026-08-30T23:59:00Z",
                first_detected_missing="2026-08-31T08:00:00Z",
                hours_remaining=27.5,
            )
        ],
        attendance_summary=DailyAttendanceSummary(
            date="2026-08-31",
            total_anomalies=1,
            records=[
                AttendancePeriodRecord(
                    period=2,
                    course_name="Pre-Calculus",
                    status="TARDY",
                    description="Arrived 10 minutes late",
                )
            ],
        ),
        alerts_dispatched_today=0,
        zero_alert_confirmed=True,
    )

    renderer = NotificationRenderer()
    html, text = renderer.compile_heartbeat_email(payload)

    # Verify key sections in HTML
    assert "Daily Heartbeat &amp; System Activity Briefing" in html or "Daily Heartbeat" in html
    assert "Jane Doe" in html
    assert "2026-08-31" in html
    assert "OPERATIONAL" in html
    assert "DEGRADED" in html
    assert "Physics Lab Report" in html
    assert "27.5 hours" in html
    assert "Pre-Calculus" in html
    assert "TARDY" in html
    assert "ZERO Critical Alerts Dispatched Today" in html

    # Verify text fallback
    assert "DAILY HEARTBEAT & SYSTEM ACTIVITY BRIEFING" in text
    assert "Jane Doe" in text
    assert "Physics Lab Report" in text
    assert "27.5 hours" in text
    assert "Pre-Calculus" in text
    assert "TARDY" in text


def test_heartbeat_telemetry_collection():
    mock_db = MagicMock()
    mock_state_engine = MagicMock()
    mock_authority = MagicMock()

    # Mock late submissions for grace period watchlist
    mock_state_engine.get_late_submissions.return_value = [
        TrackedAssignment(
            title="Math Homework 5",
            course_id="math_1",
            due_at="2026-08-31T12:00:00Z",
            submission_type="online_upload",
            status=AssignmentStatus.GRACE_PERIOD.value,
            first_detected_missing="2026-08-31T08:00:00Z",
            alert_dispatched=False,
        )
    ]
    mock_authority.calculate_weekday_elapsed_hours.return_value = 10.0
    mock_state_engine.get_dispatched_alerts.return_value = []

    generator = HeartbeatBriefingGenerator(
        db_client=mock_db,
        state_engine=mock_state_engine,
        authority_engine=mock_authority,
    )

    payload = generator.collect_telemetry(student_id="student_456", date="2026-08-31")

    assert payload.student_id == "student_456"
    assert payload.date == "2026-08-31"
    assert payload.zero_alert_confirmed is True
    assert len(payload.grace_watchlist) == 1
    assert payload.grace_watchlist[0].title == "Math Homework 5"
    assert payload.grace_watchlist[0].hours_remaining == 26.0


def test_heartbeat_generator_dispatch_success():
    mock_db = MagicMock()
    mock_router = MagicMock()
    mock_renderer = MagicMock()
    mock_state_engine = MagicMock()

    # Mock doc exists check for idempotency (False)
    mock_doc = MagicMock()
    mock_doc.exists = False
    mock_db.collection.return_value.document.return_value.get.return_value = mock_doc

    mock_state_engine.get_late_submissions.return_value = []
    mock_state_engine.get_dispatched_alerts.return_value = []

    mock_renderer.compile_heartbeat_email.return_value = (
        "<html>Heartbeat</html>",
        "Heartbeat Text",
    )

    mock_dispatch_result = MagicMock()
    mock_dispatch_result.success = True
    mock_dispatch_result.message_id = "msg_789"
    mock_dispatch_result.timestamp = "2026-08-31T18:00:00Z"
    mock_dispatch_result.dry_run = False
    mock_router.client.send_email.return_value = mock_dispatch_result

    generator = HeartbeatBriefingGenerator(
        db_client=mock_db,
        router=mock_router,
        renderer=mock_renderer,
        state_engine=mock_state_engine,
    )

    res = generator.generate_and_dispatch(
        student_id="student_123",
        recipient_email="parent@example.com",
        student_name="Jane Doe",
        date="2026-08-31",
    )

    assert res.success is True
    assert res.message_id == "msg_789"
    mock_router.client.send_email.assert_called_once()
