"""
Unit tests for Phase 1.9 Daily Evening Homework & Deadline Snapshot.
"""

import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import MagicMock

from src.notifications.models import (
    HomeworkSnapshotPayload,
    UpcomingDeadlineItem,
    GracePeriodSnapshotItem,
    RecentlyCompletedItem,
)
from src.notifications.homework_snapshot import HomeworkSnapshotGenerator
from src.notifications.renderer import NotificationRenderer


@pytest.fixture
def mock_db_client():
    client = MagicMock()
    # Default ledger check returning None (not sent today)
    client.get_document.return_value = None
    return client


@pytest.fixture
def mock_router():
    router = MagicMock()
    result = MagicMock()
    result.success = True
    result.status_code = 200
    result.message_id = "msg-snapshot-123"
    router.dispatch.return_value = result
    return router


def test_homework_snapshot_models():
    item_up = UpcomingDeadlineItem(
        assignment_id="a1",
        course="AP Physics",
        title="Lab Report",
        portal="Canvas",
        due_at="2026-09-02T23:59:00Z",
        submitted=False,
    )
    item_grace = GracePeriodSnapshotItem(
        assignment_id="a2",
        course="English Lit",
        title="Essay draft",
        original_due_at="2026-08-31T23:59:00Z",
        grace_expires_at="2026-09-02T23:59:00Z",
        hours_remaining=12.5,
        submission_url="https://canvas.example.com/assignments/a2",
    )
    item_comp = RecentlyCompletedItem(
        assignment_id="a3",
        course="Calculus BC",
        title="Problem Set 4",
        submitted_at="2026-09-01T14:30:00Z",
        portal="Canvas",
    )

    payload = HomeworkSnapshotPayload(
        student_id="s123",
        student_name="Alex Napier",
        generated_at="2026-09-01T19:00:00Z",
        upcoming_deadlines=[item_up],
        grace_period_items=[item_grace],
        recently_completed=[item_comp],
    )

    assert payload.student_id == "s123"
    assert len(payload.upcoming_deadlines) == 1
    assert len(payload.grace_period_items) == 1
    assert len(payload.recently_completed) == 1


def test_collect_snapshot_data_filtering(mock_db_client):
    now = datetime(2026, 9, 1, 19, 0, 0, tzinfo=timezone.utc)
    due_in_30h = (now + timedelta(hours=30)).isoformat()
    due_in_60h = (now + timedelta(hours=60)).isoformat()
    submitted_10h_ago = (now - timedelta(hours=10)).isoformat()

    # Mock assignments in db
    mock_db_client.query_collection.side_effect = lambda coll, **kwargs: {
        "assignments": [
            {
                "assignment_id": "a1",
                "course": "Math",
                "title": "HW 1",
                "due_at": due_in_30h,
                "portal": "Canvas",
                "canvas_status": "unsubmitted",
            },
            {
                "assignment_id": "a2",
                "course": "History",
                "title": "Reading",
                "due_at": due_in_60h,  # Outside 48h window
                "portal": "PowerSchool",
                "canvas_status": "unsubmitted",
            },
            {
                "assignment_id": "a3",
                "course": "Chemistry",
                "title": "Lab Quiz",
                "submitted_at": submitted_10h_ago,
                "canvas_status": "submitted",
                "portal": "Canvas",
            },
        ],
        "grace_period_items": [
            {
                "assignment_id": "g1",
                "course": "Spanish",
                "title": "Vocab Quiz",
                "original_due_at": (now - timedelta(hours=12)).isoformat(),
                "grace_expires_at": (now + timedelta(hours=12)).isoformat(),
                "status": "GRACE_PERIOD",
                "submission_url": "https://canvas.example.com/g1",
            }
        ],
    }.get(coll, [])

    generator = HomeworkSnapshotGenerator(db_client=mock_db_client)
    payload = generator.collect_snapshot_data("s123", snapshot_time=now)

    assert payload.student_id == "s123"
    assert len(payload.upcoming_deadlines) == 1
    assert payload.upcoming_deadlines[0].assignment_id == "a1"
    assert len(payload.grace_period_items) == 1
    assert payload.grace_period_items[0].assignment_id == "g1"
    assert payload.grace_period_items[0].hours_remaining == 12.0
    assert len(payload.recently_completed) == 1
    assert payload.recently_completed[0].assignment_id == "a3"


def test_asymmetric_authority_canvas_submission(mock_db_client):
    now = datetime(2026, 9, 1, 19, 0, 0, tzinfo=timezone.utc)
    due_tomorrow = (now + timedelta(hours=20)).isoformat()

    mock_db_client.query_collection.side_effect = lambda coll, **kwargs: {
        "assignments": [
            {
                "assignment_id": "a1",
                "course": "Biology",
                "title": "Cell Diagram",
                "due_at": due_tomorrow,
                "portal": "Canvas",
                "canvas_status": "submitted",
                "powerschool_missing": True,  # PowerSchool lists missing, but Canvas overrides!
            }
        ],
        "grace_period_items": [],
    }.get(coll, [])

    generator = HomeworkSnapshotGenerator(db_client=mock_db_client)
    payload = generator.collect_snapshot_data("s123", snapshot_time=now)

    assert len(payload.upcoming_deadlines) == 1
    assert payload.upcoming_deadlines[0].submitted is True


def test_renderer_homework_snapshot():
    renderer = NotificationRenderer()

    payload = HomeworkSnapshotPayload(
        student_id="s123",
        student_name="Alex Napier",
        generated_at="2026-09-01T19:00:00Z",
        upcoming_deadlines=[
            UpcomingDeadlineItem(
                assignment_id="a1",
                course="Algebra II",
                title="Polynomial Worksheet",
                portal="Canvas",
                due_at="2026-09-02T23:59:00Z",
                submitted=False,
            )
        ],
        grace_period_items=[
            GracePeriodSnapshotItem(
                assignment_id="g1",
                course="World History",
                title="DBQ Essay",
                original_due_at="2026-08-31T23:59:00Z",
                grace_expires_at="2026-09-02T23:59:00Z",
                hours_remaining=18.0,
                submission_url="https://canvas.school.edu/g1",
            )
        ],
        recently_completed=[
            RecentlyCompletedItem(
                assignment_id="c1",
                course="Physics",
                title="Motion Lab",
                submitted_at="2026-09-01T15:00:00Z",
                portal="Canvas",
            )
        ],
    )

    html_body, text_fallback = renderer.compile_homework_snapshot_email(payload)

    # Check HTML output
    assert "Bellmon Academic Sentinel" in html_body
    assert "Pending Grace Period Action Required (1)" in html_body
    assert "World History" in html_body
    assert "DBQ Essay" in html_body
    assert "Algebra II" in html_body
    assert "Motion Lab" in html_body
    assert "18.0h Left" in html_body

    # Check Text fallback
    assert "BELLMON HOMEWORK SNAPSHOT - ALEX NAPIER" in text_fallback
    assert "URGENT: PENDING GRACE PERIOD ITEMS" in text_fallback
    assert "DBQ Essay" in text_fallback
    assert "Polynomial Worksheet" in text_fallback


def test_generate_and_dispatch_idempotency(mock_db_client, mock_router):
    now = datetime(2026, 9, 1, 19, 0, 0, tzinfo=timezone.utc)
    generator = HomeworkSnapshotGenerator(
        db_client=mock_db_client, router=mock_router
    )

    # First dispatch succeeds
    res1 = generator.generate_and_dispatch(
        student_id="s123",
        recipient_email="parent@example.com",
        student_name="Alex",
        snapshot_time=now,
    )
    assert res1.success is True
    mock_db_client.save_document.assert_called_once()

    # Second dispatch on same day fails due to ledger idempotency key
    mock_db_client.get_document.return_value = {"sent_at": "2026-09-01T19:00:00Z"}
    res2 = generator.generate_and_dispatch(
        student_id="s123",
        recipient_email="parent@example.com",
        student_name="Alex",
        snapshot_time=now,
    )
    assert res2.success is False
    assert "already sent today" in res2.error_message.lower()
