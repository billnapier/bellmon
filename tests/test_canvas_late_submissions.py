"""
Unit and integration tests for Phase 1.6 Canvas Late Submission Tracking.
"""

from datetime import datetime, timezone, timedelta
import pytest

from src.storage.models import LateSubmissionRecord
from src.storage.firestore import FirestoreStateEngine, MockFirestoreClient
from src.ingestion.canvas import CanvasClient, CanvasSubmission, parse_iso_datetime


def test_late_submission_record_model():
    """Verify LateSubmissionRecord model defaults and validation."""
    record = LateSubmissionRecord(
        assignment_id="101",
        course_id="201",
        course_name="Algebra II",
        title="Quadratic Equations HW",
        due_at="2026-08-25T23:59:00Z",
        submitted_at="2026-08-26T08:30:00Z",
        minutes_late=511,
    )
    assert record.assignment_id == "101"
    assert record.course_id == "201"
    assert record.is_late is True
    assert record.minutes_late == 511
    assert record.detected_at is not None

    data = record.model_dump(mode="json")
    reconstructed = LateSubmissionRecord.model_validate(data)
    assert reconstructed.assignment_id == record.assignment_id
    assert reconstructed.minutes_late == 511


def test_canvas_submission_ingestion_late_true():
    """FR-001, FR-002, FR-003, Acceptance Scenario 1: Detect late submission when late=True."""
    client = CanvasClient(base_url="https://canvas.example.com", token="test_token")
    submissions = [
        CanvasSubmission(
            assignment_id=98765,
            course_id=50,
            submitted_at="2026-08-28T10:30:00Z",
            due_at="2026-08-28T08:00:00Z",
            late=True,
            seconds_late=9000,
            assignment={"name": "History Essay #1"},
        )
    ]
    course_names = {"50": "AP US History"}
    records = client.process_late_submissions("student_123", submissions, course_names)

    assert len(records) == 1
    rec = records[0]
    assert rec.assignment_id == "98765"
    assert rec.course_id == "50"
    assert rec.course_name == "AP US History"
    assert rec.title == "History Essay #1"
    assert rec.minutes_late == 150  # 9000 seconds // 60
    assert rec.is_late is True


def test_canvas_submission_submitted_after_due():
    """FR-002: Detect late submission when submitted_at > due_at even if late flag is False."""
    client = CanvasClient(base_url="https://canvas.example.com", token="test_token")
    submissions = [
        CanvasSubmission(
            assignment_id=98766,
            course_id=51,
            submitted_at="2026-08-28T09:00:00Z",
            due_at="2026-08-28T08:00:00Z",
            late=False,
            seconds_late=0,
            assignment={"name": "Lab Report 3"},
        )
    ]
    records = client.process_late_submissions("student_123", submissions)

    assert len(records) == 1
    rec = records[0]
    assert rec.assignment_id == "98766"
    assert rec.minutes_late == 60  # 1 hour late
    assert rec.is_late is True


def test_canvas_submission_timely_ignored():
    """FR-002, Acceptance Scenario 2, SC-003: Timely assignments produce 0 late submission records."""
    client = CanvasClient(base_url="https://canvas.example.com", token="test_token")
    submissions = [
        CanvasSubmission(
            assignment_id=98767,
            course_id=52,
            submitted_at="2026-08-28T07:55:00Z",
            due_at="2026-08-28T08:00:00Z",
            late=False,
            seconds_late=0,
            assignment={"name": "Math Worksheet"},
        )
    ]
    records = client.process_late_submissions("student_123", submissions)
    assert len(records) == 0


def test_canvas_submission_missing_submitted_at():
    """Edge Case: Missing submitted_at on late assignment uses detected_at timestamp."""
    client = CanvasClient(base_url="https://canvas.example.com", token="test_token")
    submissions = [
        CanvasSubmission(
            assignment_id=98768,
            course_id=53,
            submitted_at=None,
            due_at="2026-08-27T23:59:00Z",
            late=True,
            seconds_late=0,
            assignment={"name": "Unsubmitted Late Project"},
        )
    ]
    records = client.process_late_submissions("student_123", submissions)

    assert len(records) == 1
    rec = records[0]
    assert rec.assignment_id == "98768"
    assert rec.submitted_at is None
    assert rec.is_late is True
    assert rec.detected_at is not None


def test_canvas_submission_due_date_extended():
    """Edge Case: Teacher extends due date after late submission -> is_late set to False."""
    client = CanvasClient(base_url="https://canvas.example.com", token="test_token")
    submissions = [
        CanvasSubmission(
            assignment_id=98769,
            course_id=54,
            submitted_at="2026-08-28T09:00:00Z",
            due_at="2026-08-28T12:00:00Z",  # Due date extended to 12:00 (after 09:00 submission)
            late=True,  # Canvas API might still carry stale late=True
            seconds_late=0,
            assignment={"name": "Physics Homework"},
        )
    ]
    records = client.process_late_submissions("student_123", submissions)

    assert len(records) == 1
    rec = records[0]
    assert rec.assignment_id == "98769"
    assert rec.is_late is False
    assert rec.minutes_late == 0


def test_firestore_save_and_deduplication():
    """FR-004, FR-005, SC-002: Idempotent writes prevent duplicate records in Firestore."""
    mock_client = MockFirestoreClient()
    engine = FirestoreStateEngine(client=mock_client)

    rec1 = LateSubmissionRecord(
        assignment_id="assignment_98765",
        course_id="course_10",
        course_name="Biology",
        title="Cell Structure Diagram",
        due_at="2026-08-20T23:59:00Z",
        submitted_at="2026-08-21T02:00:00Z",
        minutes_late=121,
    )

    # First write
    engine.save_late_submission("student_1", rec1)

    stored = engine.get_late_submissions("student_1")
    assert len(stored) == 1
    assert stored[0].assignment_id == "assignment_98765"
    assert stored[0].minutes_late == 121

    # Second write with exact same assignment_id (re-sync run)
    rec1_updated = rec1.model_copy(update={"minutes_late": 121})
    engine.save_late_submission("student_1", rec1_updated)

    stored_after = engine.get_late_submissions("student_1")
    assert len(stored_after) == 1  # Deduplicated by document ID assignment_98765
    assert stored_after[0].assignment_id == "assignment_98765"


def test_firestore_get_late_submissions_date_filtering():
    """FR-006: Query late submissions within specified date window [start_date, end_date]."""
    mock_client = MockFirestoreClient()
    engine = FirestoreStateEngine(client=mock_client)

    records = [
        LateSubmissionRecord(
            assignment_id="a1",
            course_id="c1",
            title="Assignment 1",
            submitted_at="2026-08-10T10:00:00Z",
            minutes_late=30,
        ),
        LateSubmissionRecord(
            assignment_id="a2",
            course_id="c1",
            title="Assignment 2",
            submitted_at="2026-08-15T14:00:00Z",
            minutes_late=60,
        ),
        LateSubmissionRecord(
            assignment_id="a3",
            course_id="c1",
            title="Assignment 3",
            submitted_at="2026-08-25T09:00:00Z",
            minutes_late=90,
        ),
    ]
    engine.save_late_submissions("student_1", records)

    # Query range August 12 to August 20
    results = engine.get_late_submissions("student_1", start_date="2026-08-12", end_date="2026-08-20")
    assert len(results) == 1
    assert results[0].assignment_id == "a2"

    # Query all
    all_results = engine.get_late_submissions("student_1")
    assert len(all_results) == 3


def test_firestore_get_late_submissions_filters_non_late():
    """Verify get_late_submissions excludes records where is_late is False."""
    mock_client = MockFirestoreClient()
    engine = FirestoreStateEngine(client=mock_client)

    rec_late = LateSubmissionRecord(
        assignment_id="a1",
        course_id="c1",
        title="Late Task",
        submitted_at="2026-08-20T10:00:00Z",
        minutes_late=120,
        is_late=True,
    )
    rec_cleared = LateSubmissionRecord(
        assignment_id="a2",
        course_id="c1",
        title="Cleared Task (Due Date Extended)",
        submitted_at="2026-08-21T10:00:00Z",
        minutes_late=0,
        is_late=False,
    )
    engine.save_late_submissions("student_1", [rec_late, rec_cleared])

    active_late = engine.get_late_submissions("student_1")
    assert len(active_late) == 1
    assert active_late[0].assignment_id == "a1"
