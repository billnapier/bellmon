"""
Unit tests for GCP Cloud Firestore State Persistence Engine (using Mock client).
"""

import pytest
from datetime import datetime, timezone

from src.storage import (
    FirestoreStateEngine,
    StudentState,
    CourseState,
    GradeSnapshot,
    TrackedAssignment,
    AttendanceEvent,
    SessionCookies,
)


@pytest.fixture
def mock_engine():
    """Fixture providing a FirestoreStateEngine initialized in mock mode."""
    return FirestoreStateEngine(use_mock=True)


# --- User Story 1 Tests: Student State Document Store ---

def test_get_nonexistent_student_returns_default_state(mock_engine):
    """Scenario 1.1: Requesting nonexistent student returns clean default state."""
    state = mock_engine.get_student_state("STU-999")
    assert state.student_id == "STU-999"
    assert state.courses == {}
    assert state.tracked_assignments == {}
    assert state.attendance_events == []
    assert state.session_cookies is None


def test_update_and_get_student_state(mock_engine):
    """Scenario 1.2: Updating student state persists data correctly."""
    student_id = "STU-101"
    initial_state = StudentState(
        student_id=student_id,
        courses={
            "MATH-101": CourseState(
                name="AP Calculus AB",
                current_percentage=94.5,
                letter_grade="A",
            )
        },
        tracked_assignments={
            "HW-01": TrackedAssignment(
                title="Limits Problem Set",
                course_id="MATH-101",
                due_at="2026-08-20T23:59:00Z",
                submission_type="online_upload",
                status="missing",
                alert_dispatched=True,
            )
        },
        attendance_events=[
            AttendanceEvent(
                date="2026-08-22",
                period="1",
                course="AP Calculus AB",
                code="T",
                notified=True,
            )
        ]
    )

    mock_engine.update_student_state(student_id, initial_state)

    retrieved = mock_engine.get_student_state(student_id)
    assert retrieved.student_id == student_id
    assert "MATH-101" in retrieved.courses
    assert retrieved.courses["MATH-101"].current_percentage == 94.5
    assert "HW-01" in retrieved.tracked_assignments
    assert retrieved.tracked_assignments["HW-01"].status == "missing"
    assert len(retrieved.attendance_events) == 1
    assert retrieved.attendance_events[0].code == "T"


# --- User Story 2 Tests: Grade History Snapshot Ledger ---

def test_append_grade_snapshot(mock_engine):
    """Scenario 2.1: Appending daily grade snapshots updates history without overwriting previous snapshots."""
    student_id = "STU-202"
    course_id = "PHYS-201"

    snap1 = GradeSnapshot(date="2026-08-10", percentage=92.0, letter_grade="A-")
    snap2 = GradeSnapshot(date="2026-08-15", percentage=88.5, letter_grade="B+")
    snap3 = GradeSnapshot(date="2026-08-20", percentage=84.0, letter_grade="B")

    mock_engine.append_grade_snapshot(student_id, course_id, snap1)
    mock_engine.append_grade_snapshot(student_id, course_id, snap2)
    mock_engine.append_grade_snapshot(student_id, course_id, snap3)

    state = mock_engine.get_student_state(student_id)
    course = state.courses[course_id]
    assert course.current_percentage == 84.0
    assert course.letter_grade == "B"
    assert len(course.history) == 3
    assert [h.date for h in course.history] == ["2026-08-10", "2026-08-15", "2026-08-20"]


def test_get_grade_history_window_query(mock_engine):
    """Scenario 2.2: Historical window query returns snapshots within [start_date, end_date]."""
    student_id = "STU-202"
    course_id = "PHYS-201"

    mock_engine.append_grade_snapshot(
        student_id, course_id, GradeSnapshot(date="2026-08-01", percentage=95.0, letter_grade="A")
    )
    mock_engine.append_grade_snapshot(
        student_id, course_id, GradeSnapshot(date="2026-08-12", percentage=90.0, letter_grade="A-")
    )
    mock_engine.append_grade_snapshot(
        student_id, course_id, GradeSnapshot(date="2026-08-15", percentage=87.0, letter_grade="B+")
    )
    mock_engine.append_grade_snapshot(
        student_id, course_id, GradeSnapshot(date="2026-08-22", percentage=85.0, letter_grade="B")
    )

    history_window = mock_engine.get_grade_history(
        student_id, course_id, start_date="2026-08-10", end_date="2026-08-20"
    )
    assert len(history_window) == 2
    assert history_window[0].date == "2026-08-12"
    assert history_window[1].date == "2026-08-15"


# --- User Story 3 Tests: Session Cookie Storage & Retrieval ---

def test_save_and_get_session_cookies(mock_engine):
    """Scenario 3.1 & 3.2: Saving and reading SAML session cookies."""
    student_id = "STU-303"
    psaid_token = "encrypted_psaid_session_token_xyz123"

    # Initially None
    assert mock_engine.get_session_cookies(student_id) is None

    # Save cookies
    mock_engine.save_session_cookies(student_id, psaid_token)

    # Retrieve cookies
    cookies = mock_engine.get_session_cookies(student_id)
    assert cookies is not None
    assert cookies.psaid == psaid_token
    assert isinstance(cookies.updated_at, str)
