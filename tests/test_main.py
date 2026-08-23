"""
Unit test suite for Bellmon Batch Orchestrator entrypoint (src/main.py).
"""

import json
from unittest.mock import MagicMock, patch
import pytest

from src.main import run_batch, main, StudentSnapshot, BatchExecutionResult
from src.ingestion.canvas import CanvasCourse, CanvasAssignment
from src.ingestion.powerschool import PowerSchoolCourse, AttendanceRecord


def test_run_batch_full_success(capsys):
    mock_canvas = MagicMock()
    mock_canvas.get_courses.return_value = [
        CanvasCourse(id=101, name="AP Calculus BC", course_code="MATH101")
    ]
    mock_canvas.get_missing_submissions.return_value = [
        CanvasAssignment(id=201, name="Limits Homework", course_id=101)
    ]

    mock_powerschool = MagicMock()
    mock_powerschool.run_browser_session.return_value = {
        "courses": [
            PowerSchoolCourse(course_code="MATH101", name="AP Calculus BC", letter_grade="A", percentage=95.5)
        ],
        "attendance": [
            AttendanceRecord(date="2026-08-20", period="P1", course="AP Calculus BC", code="T")
        ]
    }

    snapshot, result = run_batch(
        student_id="student_123",
        canvas_client=mock_canvas,
        powerschool_scraper=mock_powerschool
    )

    assert isinstance(snapshot, StudentSnapshot)
    assert isinstance(result, BatchExecutionResult)
    assert result.status == "SUCCESS"
    assert result.canvas_status == "SUCCESS"
    assert result.powerschool_status == "SUCCESS"
    assert len(snapshot.canvas_courses) == 1
    assert len(snapshot.powerschool_courses) == 1
    assert len(snapshot.missing_assignments) == 1
    assert len(snapshot.attendance_events) == 1

    captured = capsys.readouterr()
    assert "student_snapshot" in captured.out
    assert "batch_execution_result" in captured.out


def test_run_batch_partial_failure(capsys):
    mock_canvas = MagicMock()
    mock_canvas.get_courses.return_value = [
        CanvasCourse(id=101, name="AP Physics C", course_code="PHYS101")
    ]
    mock_canvas.get_missing_submissions.return_value = []

    mock_powerschool = MagicMock()
    mock_powerschool.run_browser_session.side_effect = Exception("SAML Auth Timeout")

    snapshot, result = run_batch(
        student_id="student_123",
        canvas_client=mock_canvas,
        powerschool_scraper=mock_powerschool
    )

    assert result.status == "PARTIAL_FAILURE"
    assert result.canvas_status == "SUCCESS"
    assert result.powerschool_status == "FAILURE"
    assert "SAML Auth Timeout" in result.error_message
    assert len(snapshot.canvas_courses) == 1
    assert len(snapshot.powerschool_courses) == 0


def test_run_batch_total_failure(capsys):
    mock_canvas = MagicMock()
    mock_canvas.get_courses.side_effect = Exception("Canvas 500 Error")

    mock_powerschool = MagicMock()
    mock_powerschool.run_browser_session.side_effect = Exception("PowerSchool 503 Error")

    snapshot, result = run_batch(
        student_id="student_123",
        canvas_client=mock_canvas,
        powerschool_scraper=mock_powerschool
    )

    assert result.status == "FAILURE"
    assert result.canvas_status == "FAILURE"
    assert result.powerschool_status == "FAILURE"
    assert "Canvas 500 Error" in result.error_message
    assert "PowerSchool 503 Error" in result.error_message


@patch("src.main.run_batch")
def test_main_cli_exit_code_success(mock_run_batch):
    mock_result = BatchExecutionResult(
        timestamp="2026-08-23T00:00:00Z",
        status="SUCCESS",
        canvas_status="SUCCESS",
        powerschool_status="SUCCESS",
        duration_seconds=1.5
    )
    mock_snapshot = StudentSnapshot(student_id="test", timestamp="2026-08-23T00:00:00Z")
    mock_run_batch.return_value = (mock_snapshot, mock_result)

    assert main() == 0


@patch("src.main.run_batch")
def test_main_cli_exit_code_failure(mock_run_batch):
    mock_result = BatchExecutionResult(
        timestamp="2026-08-23T00:00:00Z",
        status="FAILURE",
        canvas_status="FAILURE",
        powerschool_status="FAILURE",
        duration_seconds=1.5,
        error_message="Total failure"
    )
    mock_snapshot = StudentSnapshot(student_id="test", timestamp="2026-08-23T00:00:00Z")
    mock_run_batch.return_value = (mock_snapshot, mock_result)

    assert main() == 1
