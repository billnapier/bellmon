# Data Model Specification: Phase 0.4 Containerized Cloud Run Batch Runner

**Feature Branch**: `004-phase-0-4-batch-runner-poc`  
**Date**: 2026-08-23  

## Key Entities & Data Schemas

### 1. BatchExecutionResult
Represents execution telemetry and status for a single batch runner execution run.

```python
class BatchExecutionResult(BaseModel):
    timestamp: str          # ISO 8601 UTC timestamp
    status: str             # "SUCCESS" | "PARTIAL_FAILURE" | "FAILURE"
    canvas_status: str      # "SUCCESS" | "FAILURE" | "SKIPPED"
    powerschool_status: str # "SUCCESS" | "FAILURE" | "SKIPPED"
    duration_seconds: float # Execution time in seconds
    error_message: Optional[str] = None
```

### 2. StudentSnapshot
Represents the unified harvested student performance snapshot containing Canvas and PowerSchool telemetry.

```python
class StudentSnapshot(BaseModel):
    student_id: str
    timestamp: str
    canvas_courses: List[CanvasCourse] = []
    powerschool_courses: List[PowerSchoolCourse] = []
    missing_assignments: List[AssignmentRecord] = []
    attendance_events: List[AttendanceRecord] = []
```

## State Transitions & Failures

- **Full Success**: Both Canvas and PowerSchool ingestion succeed -> `status = "SUCCESS"`, exit code 0.
- **Partial Failure**: Canvas succeeds but PowerSchool fails (or vice versa) -> `status = "PARTIAL_FAILURE"`, partial snapshot logged to stdout, exit code 0 (or log error metric without ungraceful crash).
- **Total Failure**: Both Canvas and PowerSchool fail -> `status = "FAILURE"`, error logged to Cloud Logging, non-zero exit code (1).
