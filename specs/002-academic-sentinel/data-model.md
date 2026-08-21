# Data Model: Academic & Workload Sentinel

**Feature**: `002-academic-sentinel`  
**Date**: 2026-08-20  

## Key Entities & Schemas

### 1. Student Document (`students/{student_id}`)

| Field | Type | Description | Validation |
| :--- | :--- | :--- | :--- |
| `student_id` | String | Primary unique identifier | Non-empty |
| `name` | String | Student full name | Non-empty |
| `last_synced_at` | Timestamp | Timestamp of last successful sync run | ISO-8601 |
| `courses` | Map<String, CourseSnapshot> | Keyed by course code (e.g. `ENG101`) | Valid object |

### 2. Course Snapshot (`CourseSnapshot`)

| Field | Type | Description | Validation |
| :--- | :--- | :--- | :--- |
| `course_code` | String | Unique course identifier | e.g., `ENG101` |
| `name` | String | Course display name | Non-empty |
| `current_percentage` | Float | Latest overall percentage grade | $0.0 - 100.0$ |
| `letter_grade` | String | Current letter grade | e.g. `A-`, `B+` |
| `grade_history` | Array<GradeSnapshot> | Rolling daily percentage snapshots (14-day history) | Max 14 items |

### 3. Tracked Assignment Document (`tracked_assignments/{assignment_id}`)

| Field | Type | Description | Validation |
| :--- | :--- | :--- | :--- |
| `assignment_id` | String | Unique ID (`canvas_{id}` or `ps_{id}`) | Non-empty |
| `title` | String | Assignment title | Non-empty |
| `course_id` | String | Associated course identifier | Non-empty |
| `due_at` | Timestamp | Assignment due date and time | ISO-8601 |
| `submission_type` | String | `online_upload`, `on_paper`, `none`, `discussion` | Enum |
| `canvas_missing` | Boolean | Missing flag from Canvas API | Boolean |
| `powerschool_status` | String | `unrecorded`, `collected`, `missing`, `graded` | Enum |
| `points_possible` | Float | Maximum assignment points | $\ge 0.0$ |
| `score` | Float | Earned points | Optional float |
| `first_detected_missing` | Timestamp | Timestamp when first detected missing | ISO-8601 |
| `state` | String | `GRACE_PERIOD`, `ALERT_DISPATCHED`, `RESOLVED`, `SUPPRESSED` | Enum |

### 4. Attendance Record (`attendance_events/{event_id}`)

| Field | Type | Description | Validation |
| :--- | :--- | :--- | :--- |
| `event_id` | String | Unique composite key (`{student_id}_{date}_{period}`) | Non-empty |
| `date` | String | Attendance date (`YYYY-MM-DD`) | ISO Date |
| `period` | Integer | Class period number | $\ge 1$ |
| `course` | String | Course display name | Non-empty |
| `code` | String | Attendance code (`A`, `T`, `U`, `CUT`) | Enum |
| `notified` | Boolean | Notification dispatch status | Boolean |

### 5. Alert Ledger Document (`alert_ledger/{ledger_id}`)

| Field | Type | Description | Validation |
| :--- | :--- | :--- | :--- |
| `ledger_id` | String | Unique event key for idempotency | Non-empty |
| `event_type` | String | `MISSING_WORK`, `GRADE_DROP`, `ATTENDANCE_ANOMALY` | Enum |
| `student_id` | String | Target student ID | Non-empty |
| `dispatched_at` | Timestamp | Dispatch timestamp | ISO-8601 |
| `payload_hash` | String | Hash of dispatched alert body | SHA-256 |
