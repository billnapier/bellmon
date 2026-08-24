# Data Models: Phase 1.5 SendGrid Responsive Email Router

## 1. Notification Models (`src/notifications/models.py`)

### `EmailPayload`
Represents the compiled email payload ready for delivery.

| Field | Type | Description |
|-------|------|-------------|
| `recipient_email` | `str` | Destination email address |
| `recipient_name` | `Optional[str]` | Parent / Guardian display name |
| `student_name` | `str` | Student display name / ID |
| `subject` | `str` | Email subject line |
| `html_body` | `str` | Compiled responsive HTML email body |
| `text_fallback` | `str` | Plaintext fallback body |
| `missing_work_alerts` | `List[PendingAlert]` | List of confirmed missing work alerts |
| `grade_drop_alerts` | `List[GradeVelocityDrop]` | List of grade velocity drop alerts |
| `attendance_alerts` | `List[AttendanceEvent]` | List of urgent attendance anomaly alerts |

### `DispatchResult`
Represents the outcome of an email dispatch attempt.

| Field | Type | Description |
|-------|------|-------------|
| `success` | `bool` | True if email was accepted by SendGrid API or simulated in dry-run |
| `message_id` | `Optional[str]` | Unique SendGrid message ID or simulated dry-run UUID |
| `recipient` | `str` | Destination email address |
| `timestamp` | `str` | ISO 8601 UTC timestamp of dispatch attempt |
| `error_message` | `Optional[str]` | Error details if dispatch failed |
| `dry_run` | `bool` | True if delivery was simulated locally |

---

## 2. Updated Batch Execution Models (`src/main.py`)

### `BatchExecutionResult` (Extended)

| Field | Type | Description |
|-------|------|-------------|
| `timestamp` | `str` | Execution start timestamp |
| `status` | `str` | `"SUCCESS"` \| `"PARTIAL_FAILURE"` \| `"FAILURE"` |
| `canvas_status` | `str` | Ingestion status |
| `powerschool_status` | `str` | Ingestion status |
| `alerts_generated` | `int` | Count of total P0 alerts emitted across all engines |
| `email_status` | `str` | `"DISPATCHED"` \| `"DRY_RUN"` \| `"SKIPPED"` \| `"FAILURE"` |
| `duration_seconds` | `float` | Total execution runtime |
| `error_message` | `Optional[str]` | Aggregated error log |
