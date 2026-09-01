"""
Bellmon Unified Batch Orchestrator Entrypoint (Phase 0.4 & Phase 2.3).

Sequentially executes Canvas LMS API ingestion and PowerSchool SIS Playwright scraping,
aggregating telemetry into StudentSnapshot and BatchExecutionResult JSON records printed to stdout.
Integrates WorkloadRadarEngine and SundayDigestRouter for Sunday Evening Digest dispatching.
"""

import sys
import json
import time
import logging
from datetime import datetime, timezone
from typing import Optional, Tuple, List, Dict, Any
from pydantic import BaseModel, Field

from src.ingestion.canvas import CanvasClient, CanvasCourse, CanvasAssignment
from src.ingestion.powerschool import PowerSchoolScraper, PowerSchoolCourse, AttendanceRecord
from src.radar.engine import WorkloadRadarEngine
from src.notifications.digest import SundayDigestPayload, SundayDigestRenderer, SundayDigestRouter
from src.notifications.resend import ResendClient
from src.notifications.models import EmailPayload

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(name)s - %(message)s")
logger = logging.getLogger("bellmon.batch_runner")


class StudentSnapshot(BaseModel):
    """Harvested data snapshot combining Canvas and PowerSchool telemetry."""
    student_id: str
    timestamp: str
    canvas_courses: List[CanvasCourse] = Field(default_factory=list)
    powerschool_courses: List[PowerSchoolCourse] = Field(default_factory=list)
    missing_assignments: List[CanvasAssignment] = Field(default_factory=list)
    attendance_events: List[AttendanceRecord] = Field(default_factory=list)


class BatchExecutionResult(BaseModel):
    """Batch execution telemetry record for monitoring and logging."""
    timestamp: str
    status: str  # "SUCCESS" | "PARTIAL_FAILURE" | "FAILURE"
    canvas_status: str  # "SUCCESS" | "FAILURE" | "SKIPPED"
    powerschool_status: str  # "SUCCESS" | "FAILURE" | "SKIPPED"
    duration_seconds: float
    error_message: Optional[str] = None


class SundayBatchExecutionLog(BaseModel):
    """Structured log record for Sunday batch executions."""
    timestamp: str
    is_sunday_run: bool
    radar_clumping_found: bool
    digest_dispatched: bool
    resend_id: Optional[str] = None
    errors: List[str] = Field(default_factory=list)


from src.storage.models import StudentPreferences

def run_batch(
    student_id: str = "default_student",
    canvas_client: Optional[CanvasClient] = None,
    powerschool_scraper: Optional[PowerSchoolScraper] = None,
    resend_client: Optional[ResendClient] = None,
    recipient_email: str = "parent@example.com",
    now_override: Optional[datetime] = None,
    force_sunday: bool = False,
    assignments_override: Optional[List[Dict[str, Any]]] = None,
    preferences: Optional[StudentPreferences] = None,
) -> Tuple[StudentSnapshot, BatchExecutionResult]:
    """
    Executes sequential ingestion for Canvas LMS and PowerSchool SIS.
    On Sundays, triggers WorkloadRadarEngine and dispatches Sunday Evening Digest via Resend.
    Outputs structured JSON records to stdout.
    """
    start_time = time.time()
    now_dt = now_override or datetime.now(timezone.utc)
    if now_dt.tzinfo is None:
        now_dt = now_dt.replace(tzinfo=timezone.utc)
    now_iso = now_dt.isoformat()

    snapshot = StudentSnapshot(student_id=student_id, timestamp=now_iso)
    
    canvas_status = "SKIPPED"
    powerschool_status = "SKIPPED"
    errors: List[str] = []

    # 1. Canvas LMS REST API Ingestion
    try:
        logger.info("Starting Canvas LMS REST API ingestion...")
        client = canvas_client or CanvasClient()
        snapshot.canvas_courses = client.get_courses()
        snapshot.missing_assignments = client.get_missing_submissions(observee_id="self")
        canvas_status = "SUCCESS"
        logger.info(f"Canvas LMS ingestion completed successfully. Courses: {len(snapshot.canvas_courses)}, Missing: {len(snapshot.missing_assignments)}")
    except Exception as err:
        canvas_status = "FAILURE"
        error_msg = f"Canvas ingestion failed: {err}"
        errors.append(error_msg)
        logger.error(error_msg)

    # 2. PowerSchool SIS Playwright Scraping
    try:
        logger.info("Starting PowerSchool SIS Playwright scraping...")
        scraper = powerschool_scraper or PowerSchoolScraper(student_id=student_id)
        ps_data = scraper.run_browser_session()
        snapshot.powerschool_courses = ps_data.get("courses", [])
        snapshot.attendance_events = ps_data.get("attendance", [])
        powerschool_status = "SUCCESS"
        logger.info(f"PowerSchool SIS ingestion completed successfully. Courses: {len(snapshot.powerschool_courses)}, Attendance events: {len(snapshot.attendance_events)}")
    except Exception as err:
        powerschool_status = "FAILURE"
        error_msg = f"PowerSchool ingestion failed: {err}"
        errors.append(error_msg)
        logger.error(error_msg)

    # Calculate duration & status
    duration = round(time.time() - start_time, 2)
    
    if canvas_status == "SUCCESS" and powerschool_status == "SUCCESS":
        overall_status = "SUCCESS"
    elif canvas_status == "SUCCESS" or powerschool_status == "SUCCESS":
        overall_status = "PARTIAL_FAILURE"
    else:
        overall_status = "FAILURE"

    execution_result = BatchExecutionResult(
        timestamp=now_iso,
        status=overall_status,
        canvas_status=canvas_status,
        powerschool_status=powerschool_status,
        duration_seconds=duration,
        error_message="; ".join(errors) if errors else None,
    )

    # Log JSON snapshot and result payloads to stdout for GCP Cloud Logging
    print(json.dumps({"type": "student_snapshot", "data": snapshot.model_dump(mode="json")}))
    print(json.dumps({"type": "batch_execution_result", "data": execution_result.model_dump(mode="json")}))

    # 3. Sunday Evening Planning Digest & Workload Radar Integration
    digest_router = SundayDigestRouter()
    is_sunday = force_sunday or digest_router.should_send_digest(now=now_dt)

    if is_sunday:
        logger.info("Sunday batch trigger active: Initiating Workload Radar and Sunday Digest pipeline...")
        
        # Build assignment dicts for WorkloadRadarEngine
        if assignments_override is not None:
            radar_assignments = assignments_override
        else:
            radar_assignments = []
            for item in snapshot.missing_assignments:
                radar_assignments.append({
                    "id": getattr(item, "id", "assignment"),
                    "title": getattr(item, "name", "Untitled Assignment"),
                    "course_name": f"Course {getattr(item, 'course_id', '')}",
                    "due_at": getattr(item, "due_at", None),
                    "points_possible": getattr(item, "points_possible", 0.0),
                    "has_submitted": False,
                })

        radar_engine = WorkloadRadarEngine(preferences=preferences)
        radar_result = radar_engine.evaluate(radar_assignments, now=now_dt)

        # Build course standings
        course_standings = []
        for c in snapshot.powerschool_courses:
            if isinstance(c, dict):
                course_standings.append({
                    "course_name": c.get("name") or c.get("course_name", "Unknown Course"),
                    "grade_letter": c.get("letter_grade") or c.get("grade_letter", "N/A"),
                    "grade_percent": c.get("percentage") or c.get("grade_percent", 0.0),
                    "teacher_name": c.get("teacher_name", "N/A"),
                })
            elif hasattr(c, "name") or hasattr(c, "course_name"):
                course_standings.append({
                    "course_name": getattr(c, "name", getattr(c, "course_name", "Unknown")),
                    "grade_letter": getattr(c, "letter_grade", getattr(c, "grade_letter", "N/A")),
                    "grade_percent": getattr(c, "percentage", getattr(c, "grade_percent", 0.0)),
                    "teacher_name": getattr(c, "teacher_name", "N/A"),
                })

        # Calculate attendance counts
        tardy_count = 0
        unverified_count = 0
        for att in snapshot.attendance_events:
            code = getattr(att, "code", None) if hasattr(att, "code") else (att.get("code") if isinstance(att, dict) else None)
            if code == "T":
                tardy_count += 1
            elif code == "U":
                unverified_count += 1

        upcoming_deadlines = [
            {
                "title": a.get("title"),
                "course_name": a.get("course_name"),
                "due_at": str(a.get("due_at")),
                "points_possible": a.get("points_possible", 0),
            }
            for a in radar_assignments if a.get("title")
        ]

        payload = SundayDigestPayload(
            student_name=student_id,
            digest_date=now_dt,
            course_standings=course_standings,
            workload_radar=radar_result,
            upcoming_deadlines=upcoming_deadlines,
            attendance_records=[a.model_dump() if hasattr(a, "model_dump") else a for a in snapshot.attendance_events],
            tardy_count=tardy_count,
            unverified_count=unverified_count,
            late_submissions=[],
            late_count=0,
            has_late_warning=False,
        )

        renderer = SundayDigestRenderer()
        html_body = renderer.render_html(payload)
        text_body = renderer.render_text(payload)

        r_client = resend_client or ResendClient()
        email_payload = EmailPayload(
            recipient_email=recipient_email,
            student_name=student_id,
            subject=f"Bellmon Weekly Planning Digest - {student_id}",
            html_body=html_body,
            text_fallback=text_body,
        )

        resend_errors = []
        try:
            dispatch_res = r_client.send_email(email_payload)
            digest_dispatched = dispatch_res.success
            msg_id = dispatch_res.message_id
            if dispatch_res.error_message:
                resend_errors.append(dispatch_res.error_message)
        except Exception as res_err:
            logger.error(f"Failed to dispatch Sunday Digest via Resend: {res_err}")
            digest_dispatched = False
            msg_id = None
            resend_errors.append(str(res_err))

        sunday_log = SundayBatchExecutionLog(
            timestamp=now_iso,
            is_sunday_run=True,
            radar_clumping_found=radar_result.has_clumping,
            digest_dispatched=digest_dispatched,
            resend_id=msg_id,
            errors=resend_errors,
        )
        print(json.dumps({"type": "sunday_batch_execution_log", "data": sunday_log.model_dump(mode="json")}))

    return snapshot, execution_result


def main() -> int:
    """Main CLI entrypoint for batch execution."""
    logger.info("Initializing Bellmon Sentinel Batch Orchestrator...")
    _, result = run_batch()
    
    if result.status == "FAILURE":
        logger.critical("Batch runner failed completely for both ingestion systems.")
        return 1
    
    logger.info(f"Batch runner completed with status: {result.status} in {result.duration_seconds}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())

