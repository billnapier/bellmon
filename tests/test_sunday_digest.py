"""Unit tests for Sunday Evening Weekly Planning Digest (Spec 012)."""

from datetime import datetime, timezone, timedelta
import pytest

from src.radar.models import WorkloadRadarResult, WorkloadCluster, AssessmentSummary
from src.notifications.digest import (
    SundayDigestPayload,
    SundayDigestRenderer,
    SundayDigestRouter,
)


def test_sunday_digest_payload_defaults():
    payload = SundayDigestPayload(student_name="Jane Doe")
    assert payload.student_name == "Jane Doe"
    assert payload.course_standings == []
    assert payload.workload_radar is None
    assert payload.upcoming_deadlines == []
    assert payload.attendance_records == []
    assert payload.tardy_count == 0
    assert payload.unverified_count == 0


def test_sunday_digest_renderer_without_radar():
    payload = SundayDigestPayload(
        student_name="Jane Doe",
        digest_date=datetime(2026, 8, 23, 18, 0, tzinfo=timezone.utc),
        course_standings=[
            {"course_name": "AP Physics", "grade_letter": "A", "grade_percent": 95.5, "teacher_name": "Dr. Smith"},
            {"course_name": "Pre-Calculus", "grade_letter": "B+", "grade_percent": 88.0, "teacher_name": "Mr. Jones"},
        ],
        workload_radar=WorkloadRadarResult(has_clumping=False, evaluated_at=datetime.now(timezone.utc), clusters=[]),
        upcoming_deadlines=[
            {"title": "Lab Report", "course_name": "AP Physics", "due_at": "2026-08-25 23:59", "points_possible": 50}
        ],
        tardy_count=1,
        unverified_count=0,
    )
    renderer = SundayDigestRenderer()
    html = renderer.render_html(payload)
    text = renderer.render_text(payload)

    # Radar warning banner should NOT be present
    assert "Workload Clumping Radar Alert" not in html
    assert "*** WORKLOAD CLUMPING RADAR WARNING ***" not in text

    # Standings, deadlines, attendance should be present
    assert "AP Physics" in html
    assert "95.5%" in html
    assert "Dr. Smith" in html
    assert "Lab Report" in html
    assert "Tardies logged past 7 days: <strong>1</strong>" in html

    assert "AP Physics: A (95.5%)" in text
    assert "Lab Report" in text
    assert "Tardies (past 7 days): 1" in text


def test_sunday_digest_renderer_with_radar_clumping():
    cluster = WorkloadCluster(
        start_time=datetime(2026, 8, 25, 10, 0, tzinfo=timezone.utc),
        end_time=datetime(2026, 8, 26, 15, 0, tzinfo=timezone.utc),
        courses=["AP Physics", "Pre-Calculus"],
        assessments=[
            AssessmentSummary(id="a1", title="Midterm Exam", course_name="AP Physics", due_at=datetime(2026, 8, 25, 10, 0, tzinfo=timezone.utc), points_possible=100.0, is_major=True),
            AssessmentSummary(id="a2", title="Unit 2 Test", course_name="Pre-Calculus", due_at=datetime(2026, 8, 26, 15, 0, tzinfo=timezone.utc), points_possible=80.0, is_major=True),
        ],
    )
    radar_result = WorkloadRadarResult(has_clumping=True, evaluated_at=datetime.now(timezone.utc), clusters=[cluster])


    payload = SundayDigestPayload(
        student_name="Jane Doe",
        digest_date=datetime(2026, 8, 23, 18, 0, tzinfo=timezone.utc),
        course_standings=[],
        workload_radar=radar_result,
        upcoming_deadlines=[],
        tardy_count=2,
        unverified_count=1,
    )
    renderer = SundayDigestRenderer()
    html = renderer.render_html(payload)
    text = renderer.render_text(payload)

    # Radar warning banner SHOULD be present
    assert "Workload Clumping Radar Alert" in html
    assert "Midterm Exam, Unit 2 Test" in html
    assert "*** WORKLOAD CLUMPING RADAR WARNING ***" in text
    assert "Midterm Exam" in html or "AP Physics" in html


def test_sunday_digest_router_schedule_rules():
    router = SundayDigestRouter()

    # Sunday 2026-08-23 is a Sunday (weekday 6)
    sunday_1800 = datetime(2026, 8, 23, 18, 0, tzinfo=timezone.utc)
    sunday_1759 = datetime(2026, 8, 23, 17, 59, tzinfo=timezone.utc)
    monday_1800 = datetime(2026, 8, 24, 18, 0, tzinfo=timezone.utc)
    saturday_1800 = datetime(2026, 8, 22, 18, 0, tzinfo=timezone.utc)

    # 1. Sunday at 18:00 UTC with no prior send -> True
    assert router.should_send_digest(now=sunday_1800, last_sent_at=None) is True

    # 2. Sunday before 18:00 UTC -> False
    assert router.should_send_digest(now=sunday_1759, last_sent_at=None) is False

    # 3. Monday -> False
    assert router.should_send_digest(now=monday_1800, last_sent_at=None) is False

    # 4. Saturday -> False
    assert router.should_send_digest(now=saturday_1800, last_sent_at=None) is False

    # 5. Deduplication check: last sent 24h ago -> False
    last_sent_24h_ago = sunday_1800 - timedelta(hours=24)
    assert router.should_send_digest(now=sunday_1800, last_sent_at=last_sent_24h_ago) is False

    # 6. Deduplication check: last sent 50h ago -> True
    last_sent_50h_ago = sunday_1800 - timedelta(hours=50)
    assert router.should_send_digest(now=sunday_1800, last_sent_at=last_sent_50h_ago) is True
