"""
Unit tests for Bellmon Notification Router, HTML Renderer, and Resend Client.
"""

import json
import urllib.error
import pytest
from unittest.mock import patch, MagicMock

from src.notifications.models import EmailPayload, DispatchResult
from src.notifications.renderer import NotificationRenderer
from src.notifications.resend import ResendClient
from src.notifications.router import NotificationRouter
from src.engine.models import PendingMissingAlert, PendingGradeDropAlert, AlertSource
from src.storage.models import AttendanceEvent, AttendanceCodeSeverity


@pytest.fixture
def sample_alerts():
    missing_work = [
        PendingMissingAlert(
            assignment_id="hw-101",
            title="Polynomials Quiz <1>",
            course_id="Algebra II",
            due_at="2026-08-20T23:59:00Z",
            source=AlertSource.CANVAS_GRACE_EXPIRED,
            detected_at="2026-08-21T00:00:00Z",
        )
    ]
    grade_drops = [
        PendingGradeDropAlert(
            course_id="c-202",
            course_name="AP Physics",
            prev_percentage=92.5,
            curr_percentage=81.0,
            delta=11.5,
            detected_at="2026-08-24T12:00:00Z",
        )
    ]
    attendance_anomalies = [
        AttendanceEvent(
            date="2026-08-24",
            period="4",
            course_name="US History",
            code="A",
            severity=AttendanceCodeSeverity.P0_URGENT,
            description="Unexcused Absence",
        )
    ]
    return missing_work, grade_drops, attendance_anomalies


def test_notification_renderer_compiles_html_and_text(sample_alerts):
    missing_work, grade_drops, attendance = sample_alerts
    renderer = NotificationRenderer()

    html_body, text_fallback = renderer.compile_p0_email(
        student_name="Jane Doe",
        missing_work=missing_work,
        grade_drops=grade_drops,
        attendance_anomalies=attendance,
    )

    # Assert HTML content
    assert "<!DOCTYPE html>" in html_body
    assert "Jane Doe" in html_body
    assert "Polynomials Quiz &lt;1&gt;" in html_body  # HTML escaped
    assert "Algebra II" in html_body
    assert "AP Physics" in html_body
    assert "92.5% &rarr; 81.0%" in html_body
    assert "US History" in html_body
    assert "Unexcused Absence" in html_body

    # Assert Text content
    assert "BELLMON ACADEMIC SENTINEL" in text_fallback
    assert "CONFIRMED MISSING WORK (1 item(s))" in text_fallback
    assert "GRADE VELOCITY DROPS (1 item(s))" in text_fallback
    assert "ATTENDANCE ANOMALIES (1 item(s))" in text_fallback


def test_resend_client_dry_run_simulation():
    client = ResendClient(dry_run=True)
    payload = EmailPayload(
        recipient_email="parent@example.com",
        student_name="Jane Doe",
        subject="[Test Alert]",
        html_body="<p>Test</p>",
        text_fallback="Test",
    )

    result = client.send_email(payload)

    assert result.success is True
    assert result.dry_run is True
    assert result.recipient == "parent@example.com"
    assert result.message_id is not None
    assert result.message_id.startswith("simulated-")


@patch("urllib.request.urlopen")
def test_resend_client_live_dispatch_success(mock_urlopen):
    # Mock successful Resend 200/201 response with JSON body
    mock_response = MagicMock()
    mock_response.getcode.return_value = 200
    mock_response.read.return_value = json.dumps({"id": "re_123456789"}).encode("utf-8")
    mock_urlopen.return_value.__enter__.return_value = mock_response

    client = ResendClient(api_key="re_test_key", dry_run=False)
    payload = EmailPayload(
        recipient_email="parent@example.com",
        student_name="Jane Doe",
        subject="[Test Alert]",
        html_body="<p>Test</p>",
        text_fallback="Test",
    )

    result = client.send_email(payload)

    assert result.success is True
    assert result.dry_run is False
    assert result.message_id == "re_123456789"


@patch("urllib.request.urlopen")
def test_resend_client_live_dispatch_http_error(mock_urlopen):
    # Mock HTTP error response from Resend API
    mock_error = urllib.error.HTTPError(
        url="https://api.resend.com/emails",
        code=422,
        msg="Unprocessable Entity",
        hdrs={},
        fp=MagicMock(read=lambda: b'{"message": "Invalid email address"}'),
    )
    mock_urlopen.side_effect = mock_error

    client = ResendClient(api_key="re_test_key", dry_run=False)
    payload = EmailPayload(
        recipient_email="invalid-email",
        student_name="Jane Doe",
        subject="[Test Alert]",
        html_body="<p>Test</p>",
        text_fallback="Test",
    )

    result = client.send_email(payload)

    assert result.success is False
    assert result.dry_run is False
    assert "Resend HTTP 422" in result.error_message


def test_notification_router_skips_when_no_alerts():
    router = NotificationRouter(dry_run=True)
    result = router.dispatch_alerts(
        recipient_email="parent@example.com",
        student_name="Jane Doe",
        missing_work=[],
        grade_drops=[],
        attendance_anomalies=[],
    )

    assert result is None


def test_notification_router_dispatches_combined_email(sample_alerts):
    missing_work, grade_drops, attendance = sample_alerts
    router = NotificationRouter(dry_run=True)

    result = router.dispatch_alerts(
        recipient_email="parent@example.com",
        student_name="Jane Doe",
        missing_work=missing_work,
        grade_drops=grade_drops,
        attendance_anomalies=attendance,
    )

    assert result is not None
    assert result.success is True
    assert result.recipient == "parent@example.com"
    assert result.dry_run is True
