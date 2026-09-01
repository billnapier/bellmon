"""
Integration tests for Phase 2.3 Sunday Batch Orchestrator Integration.
"""

import json
from datetime import datetime, timezone
from unittest.mock import MagicMock
import pytest

from src.main import run_batch, SundayBatchExecutionLog
from src.ingestion.canvas import CanvasCourse, CanvasAssignment
from src.ingestion.powerschool import PowerSchoolCourse, AttendanceRecord
from src.notifications.resend import ResendClient


@pytest.fixture
def mock_canvas_client():
    client = MagicMock()
    client.get_courses.return_value = [
        CanvasCourse(id=101, name="AP Physics"),
        CanvasCourse(id=102, name="Calculus BC"),
    ]
    client.get_missing_submissions.return_value = [
        CanvasAssignment(
            id=1,
            name="Midterm Exam",
            course_id=101,
            due_at=datetime(2026, 9, 6, 20, 0, tzinfo=timezone.utc),
            points_possible=100.0,
        )
    ]
    return client


@pytest.fixture
def mock_powerschool_scraper():
    scraper = MagicMock()
    scraper.run_browser_session.return_value = {
        "courses": [
            PowerSchoolCourse(
                course_code="PHYS-101",
                name="AP Physics",
                letter_grade="A",
                percentage=95.0,
            )
        ],
        "attendance": [
            AttendanceRecord(date="2026-09-01", period="P1", course="AP Physics", code="T")
        ],
    }
    return scraper


def test_sunday_batch_execution_triggers_digest(
    mock_canvas_client, mock_powerschool_scraper, capsys
):
    # Sunday at 18:30 UTC
    sunday_time = datetime(2026, 9, 6, 18, 30, tzinfo=timezone.utc)
    resend_client = ResendClient(dry_run=True)

    snapshot, result = run_batch(
        student_id="test_student",
        canvas_client=mock_canvas_client,
        powerschool_scraper=mock_powerschool_scraper,
        resend_client=resend_client,
        now_override=sunday_time,
        force_sunday=True,
    )

    assert result.status == "SUCCESS"
    captured = capsys.readouterr()
    assert "sunday_batch_execution_log" in captured.out

    # Parse JSON logs
    logs = [
        json.loads(line)
        for line in captured.out.splitlines()
        if line.strip().startswith("{") and "sunday_batch_execution_log" in line
    ]
    assert len(logs) == 1
    log_data = logs[0]["data"]
    assert log_data["is_sunday_run"] is True
    assert log_data["digest_dispatched"] is True


def test_non_sunday_batch_skips_digest(
    mock_canvas_client, mock_powerschool_scraper, capsys
):
    # Monday at 10:00 UTC
    monday_time = datetime(2026, 9, 7, 10, 0, tzinfo=timezone.utc)
    resend_client = ResendClient(dry_run=True)

    snapshot, result = run_batch(
        student_id="test_student",
        canvas_client=mock_canvas_client,
        powerschool_scraper=mock_powerschool_scraper,
        resend_client=resend_client,
        now_override=monday_time,
        force_sunday=False,
    )

    assert result.status == "SUCCESS"
    captured = capsys.readouterr()
    assert "sunday_batch_execution_log" not in captured.out


def test_sunday_batch_with_clumping_radar(
    mock_canvas_client, mock_powerschool_scraper, capsys
):
    sunday_time = datetime(2026, 9, 6, 18, 0, tzinfo=timezone.utc)
    resend_client = ResendClient(dry_run=True)

    # 2 major exams due within 24h
    clumping_assignments = [
        {
            "id": "1",
            "title": "Midterm Exam 1",
            "course_name": "AP Physics",
            "due_at": datetime(2026, 9, 7, 12, 0, tzinfo=timezone.utc),
            "points_possible": 100.0,
            "has_submitted": False,
        },
        {
            "id": "2",
            "title": "Midterm Exam 2",
            "course_name": "Calculus BC",
            "due_at": datetime(2026, 9, 7, 16, 0, tzinfo=timezone.utc),
            "points_possible": 100.0,
            "has_submitted": False,
        },
    ]

    snapshot, result = run_batch(
        student_id="test_student",
        canvas_client=mock_canvas_client,
        powerschool_scraper=mock_powerschool_scraper,
        resend_client=resend_client,
        now_override=sunday_time,
        force_sunday=True,
        assignments_override=clumping_assignments,
    )

    captured = capsys.readouterr()
    logs = [
        json.loads(line)
        for line in captured.out.splitlines()
        if line.strip().startswith("{") and "sunday_batch_execution_log" in line
    ]
    assert len(logs) == 1
    assert logs[0]["data"]["radar_clumping_found"] is True


def test_ingestion_failure_fallback_on_sunday(capsys):
    failing_canvas = MagicMock()
    failing_canvas.get_courses.side_effect = Exception("Canvas Connection Error")

    failing_ps = MagicMock()
    failing_ps.run_browser_session.side_effect = Exception("PowerSchool Login Failed")

    sunday_time = datetime(2026, 9, 6, 18, 0, tzinfo=timezone.utc)
    resend_client = ResendClient(dry_run=True)

    snapshot, result = run_batch(
        student_id="test_student",
        canvas_client=failing_canvas,
        powerschool_scraper=failing_ps,
        resend_client=resend_client,
        now_override=sunday_time,
        force_sunday=True,
    )

    assert result.status == "FAILURE"
    captured = capsys.readouterr()
    assert "sunday_batch_execution_log" in captured.out
