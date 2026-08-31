# Tasks: Phase 1.8 Daily Heartbeat & System Activity Briefing

**Feature Branch**: `016-phase-1-8-daily-heartbeat-briefing`
**Status**: Complete

## Task List

- [x] **Task 1: Telemetry Data Models & Data Structures (P1)**
  - **Files**: `src/notifications/heartbeat.py`, `src/notifications/models.py`
  - **Description**: Define Pydantic models / Dataclasses for `IngestionStatus`, `GraceWatchlistItem`, `AttendanceSummary`, `AttendancePeriodRecord`, and `HeartbeatPayload`.
  - **Acceptance Criteria**:
    - `HeartbeatPayload` can serialize to dict and validate required fields.
    - Remaining hours field defaults to float value.

- [x] **Task 2: HTML Email Template Renderer for Daily Heartbeat (P1)**
  - **Files**: `src/notifications/renderer.py`
  - **Description**: Implement `compile_heartbeat_email(self, payload: HeartbeatPayload) -> Tuple[str, str]` in `NotificationRenderer`.
  - **Acceptance Criteria**:
    - HTML includes Ingestion Health Banner with green/yellow/red status indicators.
    - HTML includes Grace Period Watchlist card displaying course, title, due date, and hours remaining.
    - If zero grace items exist, renders "No active grace period items. All digital work submitted."
    - HTML includes Daily Attendance section with period breakdown and total count summary.
    - HTML includes Sentinel Standing status badge ("0 Critical Alerts Dispatched Today" or alert count).
    - Plaintext fallback contains all key telemetry sections.

- [x] **Task 3: Heartbeat Telemetry Collector & Dispatch Orchestrator (P1)**
  - **Files**: `src/notifications/heartbeat.py`
  - **Description**: Implement `HeartbeatBriefingGenerator` with Firestore state queries for ingestion status, grace period items, attendance records, and alert ledger entries.
  - **Acceptance Criteria**:
    - Calculates exact remaining grace hours using business hour elapsed time rules.
    - Prevents duplicate dispatches on the same date via `heartbeat_briefings` Firestore collection idempotency check.
    - Dispatches briefing email using `NotificationRouter`.

- [x] **Task 4: Comprehensive Unit & Integration Tests (P1)**
  - **Files**: `tests/test_heartbeat.py`
  - **Description**: Implement full test suite covering telemetry collection, HTML compilation, watchlist formatting, zero-alert standing detection, dispatch, and idempotency.
  - **Acceptance Criteria**:
    - All tests in `tests/test_heartbeat.py` pass.
    - Full test suite (`pytest`) passes without regression.

