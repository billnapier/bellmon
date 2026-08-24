# Research: Phase 1.4 Period Attendance Anomaly Sentinel

## 1. Attendance Code Severity Matrix

### Decision
Categorize PowerSchool attendance codes into three distinct severity buckets using an explicit `AttendanceCodeSeverity` Enum.

### Severity Buckets
- **`P0_URGENT`**: `A` (Unexcused Absence), `CUT` (Class Cut). Triggers immediate P0 email alert payload.
- **`P1_DIGEST`**: `T` (Tardy), `U` (Unverified). Logged to Firestore `attendance_events` with `notified: false` for Sunday digest summary; zero immediate P0 alerts.
- **`IGNORED`**: `P` (Present), `E` / `EX` (Excused Absence), `ACT` (School Activity). Suppressed completely from alert generation.

### Rationale
- Immediate notification for unexcused absences and cuts enables timely parent intervention on the same day.
- Digesting tardies and unverified records avoids spamming parents during work hours while maintaining audit trail data.
- Ignoring present and excused records avoids false alerts.

---

## 2. Event Deduplication Ledger & Key Strategy

### Decision
Deduplicate attendance events per student using a composite key `(date, period, course)`.

### Rationale
- Multiple daily batch syncs re-harvest PowerSchool attendance.
- If an attendance event matching `(date, period, course)` exists with `notified: true`, subsequent evaluations suppress duplicate P0 alerts.
- Updating an existing record's code (e.g. from `A` to `E`) updates the record in Firestore without triggering retrospective alerts.

---

## 3. Storage Integration with Firestore State Engine

### Decision
Store `attendance_events` as part of `StudentState` or `AttendanceEvent` models in `src/storage/models.py` and `src/engine/models.py`.

### Rationale
- Integrates seamlessly with the Phase 1.1 Firestore state persistence engine (`FirestoreStateEngine`).
- Enables batch execution pipeline to load student attendance history, run `AttendanceSentinel`, write back updated `attendance_events`, and return pending P0 alerts for the notification router.
