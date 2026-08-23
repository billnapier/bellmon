"""
Unit and integration tests for PowerSchool Playwright SAML SSO Scraper & Cookie Store module.
"""

import pytest
from unittest.mock import MagicMock, patch
from src.ingestion.powerschool import (
    PowerSchoolCourse,
    AttendanceRecord,
    SessionCookieStore,
    PowerSchoolScraper,
)


def test_powerschool_course_model():
    course = PowerSchoolCourse(
        course_code="MATH301",
        name="AP Calculus BC",
        letter_grade="A",
        percentage=96.5
    )
    assert course.course_code == "MATH301"
    assert course.name == "AP Calculus BC"
    assert course.letter_grade == "A"
    assert course.percentage == 96.5


def test_attendance_record_model():
    rec = AttendanceRecord(
        date="2026-08-20",
        period="P2",
        course="AP Calculus BC",
        code="A"
    )
    assert rec.date == "2026-08-20"
    assert rec.period == "P2"
    assert rec.code == "A"


def test_session_cookie_store_model():
    store = SessionCookieStore(psaid="mock_psaid_12345", updated_at="2026-08-22T10:00:00Z")
    assert store.psaid == "mock_psaid_12345"
    assert "2026-08-22" in store.updated_at


def test_resolve_credentials_env_fallback(monkeypatch):
    monkeypatch.setenv("POWERSCHOOL_USERNAME", "test_user")
    monkeypatch.setenv("POWERSCHOOL_PASSWORD", "test_pass")

    scraper = PowerSchoolScraper()
    user, pwd = scraper._resolve_credentials()

    assert user == "test_user"
    assert pwd == "test_pass"


def test_resolve_credentials_secret_manager(monkeypatch):
    monkeypatch.delenv("POWERSCHOOL_USERNAME", raising=False)
    monkeypatch.delenv("POWERSCHOOL_PASSWORD", raising=False)

    mock_secret_client = MagicMock()
    mock_payload = MagicMock()
    mock_payload.data.decode.return_value = '{"username": "sm_user", "password": "sm_password"}'
    mock_resp = MagicMock()
    mock_resp.payload = mock_payload
    mock_secret_client.access_secret_version.return_value = mock_resp

    scraper = PowerSchoolScraper(secret_client=mock_secret_client)
    user, pwd = scraper._resolve_credentials()

    assert user == "sm_user"
    assert pwd == "sm_password"


def test_get_and_save_stored_cookies_firestore():
    mock_db = MagicMock()
    mock_doc = MagicMock()
    mock_doc.exists = True
    mock_doc.to_dict.return_value = {
        "session_cookie": {
            "psaid": "stored_psaid_token",
            "updated_at": "2026-08-22T12:00:00Z"
        }
    }
    mock_doc_ref = MagicMock()
    mock_doc_ref.get.return_value = mock_doc
    mock_db.collection.return_value.document.return_value = mock_doc_ref

    scraper = PowerSchoolScraper(student_id="student_999", firestore_db=mock_db)
    cookie_store = scraper.get_stored_cookies()

    assert cookie_store is not None
    assert cookie_store.psaid == "stored_psaid_token"

    saved_store = scraper.save_stored_cookies(psaid="new_psaid_token")
    assert saved_store.psaid == "new_psaid_token"
    mock_doc_ref.set.assert_called_once()


def test_parse_guardian_html():
    sample_html = """
    <html>
        <body>
            <table class="grid">
                <tr class="course-row">
                    <td class="course-code">ENG401</td>
                    <td class="course-name">AP Literature</td>
                    <td class="letter-grade">A-</td>
                    <td class="percentage-score">92.0%</td>
                </tr>
                <tr class="course-row">
                    <td class="course-code">PHYS201</td>
                    <td class="course-name">Physics Honors</td>
                    <td class="letter-grade">B+</td>
                    <td class="percentage-score">88.5%</td>
                </tr>
            </table>
            <table class="attendance">
                <tr class="attendance-row">
                    <td>2026-08-21</td>
                    <td>P1</td>
                    <td>AP Literature</td>
                    <td>A</td>
                </tr>
                <tr class="attendance-row">
                    <td>2026-08-21</td>
                    <td>P3</td>
                    <td>Physics Honors</td>
                    <td>T</td>
                </tr>
            </table>
        </body>
    </html>
    """

    scraper = PowerSchoolScraper()
    result = scraper.parse_guardian_html(sample_html)

    courses = result["courses"]
    attendance = result["attendance"]

    assert len(courses) == 2
    assert courses[0].course_code == "ENG401"
    assert courses[0].name == "AP Literature"
    assert courses[0].letter_grade == "A-"
    assert courses[0].percentage == 92.0

    assert courses[1].course_code == "PHYS201"
    assert courses[1].percentage == 88.5

    assert len(attendance) == 2
    assert attendance[0].date == "2026-08-21"
    assert attendance[0].period == "P1"
    assert attendance[0].code == "A"
    assert attendance[1].code == "T"


def test_run_browser_session_with_mock_page():
    mock_page = MagicMock()
    mock_page.url = "https://powerschool.bcp.org/guardian/home.html"
    mock_page.query_selector.return_value = None
    mock_page.content.return_value = """
    <html>
        <body>
            <table class="grid">
                <tr class="course-row">
                    <td class="course-code">HIST101</td>
                    <td class="course-name">US History</td>
                    <td class="letter-grade">A</td>
                    <td class="percentage-score">95.0%</td>
                </tr>
            </table>
        </body>
    </html>
    """

    mock_db = MagicMock()
    mock_doc = MagicMock()
    mock_doc.exists = False
    mock_db.collection.return_value.document.return_value.get.return_value = mock_doc

    scraper = PowerSchoolScraper(student_id="student_111", firestore_db=mock_db)
    result = scraper.run_browser_session(page_override=mock_page)

    courses = result["courses"]
    assert len(courses) == 1
    assert courses[0].course_code == "HIST101"
    assert courses[0].percentage == 95.0
