"""
Bellmon Unified Batch Orchestrator Entrypoint (Phase 0.4).

Sequentially executes Canvas LMS API ingestion and PowerSchool SIS Playwright scraping,
aggregating telemetry into StudentSnapshot and BatchExecutionResult JSON records printed to stdout.
"""

import sys
import json
import time
import logging
from datetime import datetime, timezone
from typing import Optional, Tuple, List
from pydantic import BaseModel, Field

from src.ingestion.canvas import CanvasClient, CanvasCourse, CanvasAssignment
from src.ingestion.powerschool import PowerSchoolScraper, PowerSchoolCourse, AttendanceRecord

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


def run_batch(
    student_id: str = "default_student",
    canvas_client: Optional[CanvasClient] = None,
    powerschool_scraper: Optional[PowerSchoolScraper] = None,
) -> Tuple[StudentSnapshot, BatchExecutionResult]:
    """
    Executes sequential ingestion for Canvas LMS and PowerSchool SIS.
    Outputs structured JSON records to stdout.
    """
    start_time = time.time()
    now_iso = datetime.now(timezone.utc).isoformat()

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
    print(json.dumps({"type": "student_snapshot", "data": snapshot.model_dump()}, indent=2))
    print(json.dumps({"type": "batch_execution_result", "data": execution_result.model_dump()}, indent=2))

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
