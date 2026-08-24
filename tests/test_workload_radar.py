"""Unit tests for Workload Clumping Radar (Spec 011)."""

from datetime import datetime, timedelta, timezone
import pytest
from src.radar import WorkloadRadarEngine, WorkloadCluster, WorkloadRadarResult


@pytest.fixture
def engine():
    return WorkloadRadarEngine()


@pytest.fixture
def base_time():
    return datetime(2026, 8, 25, 8, 0, 0, tzinfo=timezone.utc)


def test_is_major_assessment_by_keyword(engine):
    assert engine.is_major_assessment({"title": "Unit 3 Exam", "points_possible": 20}) is True
    assert engine.is_major_assessment({"title": "Final Project Presentation", "points_possible": 15}) is True
    assert engine.is_major_assessment({"title": "Midterm Essay", "category": "General", "points_possible": 10}) is True
    assert engine.is_major_assessment({"title": "Lab 4 Report", "points_possible": 25}) is True


def test_is_major_assessment_by_points(engine):
    assert engine.is_major_assessment({"title": "Daily Homework", "points_possible": 50.0}) is True
    assert engine.is_major_assessment({"title": "Daily Homework", "points_possible": 100.0}) is True
    assert engine.is_major_assessment({"title": "Daily Homework", "points_possible": 49.9}) is False


def test_horizon_filtering(engine, base_time):
    past_due = base_time - timedelta(hours=2)
    far_future = base_time + timedelta(days=8)
    in_horizon = base_time + timedelta(days=2)

    assignments = [
        {"id": "1", "title": "Past Exam", "due_at": past_due.isoformat(), "points_possible": 100},
        {"id": "2", "title": "Far Future Exam", "due_at": far_future.isoformat(), "points_possible": 100},
        {"id": "3", "title": "Valid Exam 1", "course_name": "Math", "due_at": in_horizon.isoformat(), "points_possible": 100},
        {"id": "4", "title": "Valid Exam 2", "course_name": "Physics", "due_at": (in_horizon + timedelta(hours=10)).isoformat(), "points_possible": 100},
    ]

    result = engine.evaluate(assignments, now=base_time)

    assert result.has_clumping is True
    assert len(result.clusters) == 1
    assert len(result.clusters[0].assessments) == 2
    assert set(result.clusters[0].courses) == {"Math", "Physics"}


def test_submitted_assignments_excluded(engine, base_time):
    due_1 = base_time + timedelta(days=1)
    due_2 = base_time + timedelta(days=1, hours=5)

    assignments = [
        {"id": "1", "title": "Exam 1", "course_name": "Math", "due_at": due_1.isoformat(), "points_possible": 100, "has_submitted": True},
        {"id": "2", "title": "Exam 2", "course_name": "Physics", "due_at": due_2.isoformat(), "points_possible": 100, "has_submitted": False},
    ]

    result = engine.evaluate(assignments, now=base_time)

    # Only 1 unsubmitted exam -> no clumping
    assert result.has_clumping is False
    assert len(result.clusters) == 0


def test_clumping_window_boundary(engine, base_time):
    due_1 = base_time + timedelta(days=1)
    due_2_within = due_1 + timedelta(hours=48)  # Exactly 48h
    due_3_outside = due_1 + timedelta(hours=49)  # 49h apart

    assignments_within = [
        {"id": "1", "title": "Test 1", "course_name": "History", "due_at": due_1.isoformat(), "points_possible": 50},
        {"id": "2", "title": "Test 2", "course_name": "English", "due_at": due_2_within.isoformat(), "points_possible": 50},
    ]

    result_within = engine.evaluate(assignments_within, now=base_time)
    assert result_within.has_clumping is True
    assert len(result_within.clusters) == 1

    assignments_outside = [
        {"id": "1", "title": "Test 1", "course_name": "History", "due_at": due_1.isoformat(), "points_possible": 50},
        {"id": "2", "title": "Test 2", "course_name": "English", "due_at": due_3_outside.isoformat(), "points_possible": 50},
    ]

    result_outside = engine.evaluate(assignments_outside, now=base_time)
    assert result_outside.has_clumping is False
    assert len(result_outside.clusters) == 0
