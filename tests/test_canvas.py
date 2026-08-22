"""
Unit tests for Canvas LMS REST API Ingestion module.
"""

import pytest
from unittest.mock import MagicMock, patch
from src.ingestion.canvas import CanvasClient, CanvasCourse, CanvasAssignment


def test_canvas_course_model():
    course = CanvasCourse(id=101, name="Algebra 2 Honors", course_code="ALG2_H")
    assert course.id == 101
    assert course.name == "Algebra 2 Honors"


def test_canvas_assignment_model():
    assignment = CanvasAssignment(
        id=501,
        name="Polynomial Functions Quiz",
        course_id=101,
        points_possible=100.0,
        submission_types=["online_upload"],
        has_submitted_submissions=False,
        missing=True
    )
    assert assignment.id == 501
    assert assignment.points_possible == 100.0
    assert assignment.missing is True


@patch("requests.Session.get")
def test_get_courses_success(mock_get):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = [
        {"id": 101, "name": "Algebra 2 Honors", "course_code": "ALG2_H"},
        {"id": 102, "name": "AP Physics", "course_code": "PHYS_AP"}
    ]
    mock_get.return_value = mock_resp

    client = CanvasClient(token="mock_token")
    courses = client.get_courses()

    assert len(courses) == 2
    assert courses[0].name == "Algebra 2 Honors"
    assert courses[1].course_code == "PHYS_AP"


@patch("requests.Session.get")
def test_get_missing_submissions_success(mock_get):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "missing_submissions": [
            {
                "id": 201,
                "name": "Vectors Worksheet",
                "course_id": 102,
                "points_possible": 50.0,
                "submission_types": ["online_upload"],
                "has_submitted_submissions": False,
                "missing": True
            }
        ]
    }
    mock_get.return_value = mock_resp

    client = CanvasClient(token="mock_token")
    missing = client.get_missing_submissions(observee_id="12345")

    assert len(missing) == 1
    assert missing[0].name == "Vectors Worksheet"
    assert missing[0].course_id == 102
