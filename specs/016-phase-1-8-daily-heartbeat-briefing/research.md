# Research & Technical Decisions: Phase 1.8 Daily Heartbeat & System Activity Briefing

## 1. Ingestion Health & Portal Telemetry

### Decision
Store ingestion execution results in Firestore collection `ingestion_status` with document keys by date (`YYYY-MM-DD`) containing `canvas_status`, `powerschool_status`, `sync_timestamp`, and `error_details`.

### Rationale
- Allows `HeartbeatBriefingGenerator` to quickly read today's sync status without re-running harvesters.
- Enables clear status determination: `OPERATIONAL` if sync succeeded without error, `DEGRADED`/`FAILED` if harvester logged errors or missed execution.

### Alternatives Considered
- Direct API pinging during heartbeat generation: Rejected because heartbeat runs at 5:15 PM to summarize the 5:00 PM sync run, not to perform a new sync.

---

## 2. Grace Period Watchlist & Business Hour Remaining Calculation

### Decision
Reuse `AsymmetricAuthorityEngine` (specifically `calculate_weekday_elapsed_hours` or business hour calculation) to compute elapsed weekday business hours since assignment `due_at`. Subtract elapsed hours from total 36.0 grace period hours to yield `hours_remaining = max(0.0, round(36.0 - elapsed, 1))`.

### Rationale
- Guarantees exact alignment between sentinel escalation timers and daily briefing watchlist timers.
- Handles weekend blackouts correctly since weekend hours do not consume the 36-hour grace budget.

---

## 3. Daily Attendance Summary & Zero-Alert Standing

### Decision
Query Firestore `attendance_records` for today's date (`YYYY-MM-DD`) and `alert_ledger` entries for the current date.

### Details
- Attendance Payload: list of periods (e.g. Period 1..N), status per period (`PRESENT`, `UNEXCUSED_ABSENCE`, `TARDY`, etc.), and summary count (e.g. `6/6 Periods Present`).
- Zero-Alert Sentinel Standing: True if zero P0 alerts (missing work, grade drop, attendance anomaly) were written to `alert_ledger` on the current date; False if P0 alerts were dispatched.

---

## 4. Dispatch Scheduling & Idempotency

### Decision
Execute `HeartbeatBriefingGenerator.generate_and_dispatch` at 5:15 PM on weekdays. Store dispatch record in `heartbeat_briefings` collection indexed by student ID and date (`YYYY-MM-DD`).

### Rationale
- Idempotency key `heartbeat:{student_id}:{date}` prevents duplicate briefing emails if batch job is retried.
