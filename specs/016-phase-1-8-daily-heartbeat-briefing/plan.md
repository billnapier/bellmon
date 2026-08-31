# Implementation Plan: Phase 1.8 Daily Heartbeat & System Activity Briefing

**Feature Branch**: `016-phase-1-8-daily-heartbeat-briefing`  
**Status**: Approved  

## Technical Context & Architecture

The Daily Heartbeat & System Activity Briefing operates as a scheduled weekday 5:15 PM telemetry summary. It aggregates daily portal sync status, active grace period watchlist items, daily attendance records, and sentinel standing status into a single HTML digest.

### Components
1. `src/notifications/heartbeat.py`: Defines `HeartbeatBriefingGenerator` class and data classes (`HeartbeatPayload`, `GraceWatchlistItem`, etc.).
2. `src/notifications/renderer.py`: Extends `NotificationRenderer` with `compile_heartbeat_email(...)` to render responsive HTML and text fallback.
3. `src/notifications/router.py`: Dispatches email via `ResendNotificationRouter` / `NotificationRouter`.
4. `src/storage/firestore.py`: Firestore state queries for ingestion status, grace period assignments, attendance records, and dispatch ledger.

---

## Constitution & Architecture Checks

- **Single Source of Truth**: Uses Firestore as state store.
- **Asymmetric Grace Period Rule**: Calculates grace period remaining hours using business hour rules.
- **Idempotency**: Ledger entry stored in `heartbeat_briefings` prevents duplicate daily sends.

---

## Proposed Changes

### 1. `src/notifications/heartbeat.py`
- Class `HeartbeatBriefingGenerator`:
  - `__init__(self, db_client=None, router=None, renderer=None)`
  - `collect_telemetry(student_id: str, date: str) -> HeartbeatPayload`
  - `generate_and_dispatch(student_id: str, recipient_email: str, student_name: str, date: str) -> DispatchResult`

### 2. `src/notifications/renderer.py`
- Add method `compile_heartbeat_email(payload: HeartbeatPayload) -> Tuple[str, str]`:
  - Renders Header & Portal Status Cards (`Canvas API`, `PowerSchool Portal`).
  - Renders Grace Period Watchlist table (or empty state badge).
  - Renders Daily Attendance breakdown table and summary count.
  - Renders Sentinel Standing banner (Green zero-alert status or Red/Yellow alert count).

### 3. Tests
- `tests/test_heartbeat.py`: Unit tests for telemetry collection, grace remaining calculation, HTML rendering, dispatch, and idempotency check.

---

## Verification Plan

- Run `pytest tests/test_heartbeat.py` to verify telemetry collection, HTML compilation, and dispatch.
- Run `pytest` across full suite to prevent regression.
