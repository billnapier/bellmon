# Implementation Plan: Bellmon MVP - Core Academic Sentinel & Noise Reduction

**Feature**: Core Academic Sentinel & Noise Reduction  
**Specification**: [.specify/spec.md](../.specify/spec.md)  
**Governing Document**: [.specify/memory/constitution.md](../.specify/memory/constitution.md)  

---

## 1. Architecture Overview

```
 ┌──────────────────────┐        ┌──────────────────────┐
 │      Canvas LMS      │        │    PowerSchool SIS   │
 │   - REST API         │        │   - Mobile REST API  │
 └──────────┬───────────┘        └──────────┬───────────┘
            │                               │
            └───────────────┬───────────────┘
                            ▼
            ┌───────────────────────────────┐
            │   Scheduled Ingestion Engine  │
            │   (Python Async / Cron)       │
            └───────────────┬───────────────┘
                            ▼
            ┌───────────────────────────────┐
            │       State Store (SQLite)    │
            │  - Grade Snapshots (14 days)  │
            │  - Assignment Grace State     │
            │  - Alert Deduplication Ledger │
            └───────────────┬───────────────┘
                            ▼
            ┌───────────────────────────────┐
            │      Alert Rules Engine       │
            │  - Missing Work Matrix        │
            │  - 36h Grace Evaluator        │
            │  - Grade Drop Delta Evaluator │
            └───────────────┬───────────────┘
                            ▼
            ┌───────────────────────────────┐
            │      Notification Router      │
            │  - Pushover / NTFY Dispatch   │
            └───────────────────────────────┘
```

---

## 2. Constitution Alignment Check

| Principle | Requirement | Verification Method in Design | Status |
| :--- | :--- | :--- | :--- |
| **P1: Student Autonomy** | 36-hour delay buffer before alerting on digital missing items | Verified in `missing_work.py` by comparing `current_time - first_detected_missing >= 36h`. | ✅ PASS |
| **P2: Cross-System Noise Elimination** | Suppress alerts if PowerSchool score $>0$ or `isCollected: true` | Verified in `missing_work.py` by evaluating PS score & collection flags prior to queuing alerts. | ✅ PASS |
| **P3: Proactive Grade Velocity Drop** | Alert on 7-day rolling drop $\ge 4.0\%$ with impacting item | Verified in `trajectory.py` by comparing 7-day snapshot delta and isolating highest point loss. | ✅ PASS |
| **P4: Zero-Touch Delivery** | Unattended push dispatch via Pushover/NTFY | Verified via scheduled CLI command `bellmon sync` and `push.py` router. | ✅ PASS |
| **P5: Workload Radar** | Highlight 48h exam/project clusters in weekly digest | Deferred to Phase 2 per roadmap. | ⏩ DEFERRED |

---

## 3. Data Schema & State Storage (`bellmon/storage/db.py`)

Bellmon utilizes a lightweight SQLite database (`bellmon.db`) to track state snapshots and prevent duplicate notifications.

### 3.1 Tables Schema

```sql
-- Course grade snapshots over time
CREATE TABLE IF NOT EXISTS grade_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    course_id TEXT NOT NULL,
    course_name TEXT NOT NULL,
    percentage REAL NOT NULL,
    letter_grade TEXT,
    snapshot_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Assignment tracking state (Grace period management)
CREATE TABLE IF NOT EXISTS assignment_states (
    assignment_id TEXT PRIMARY KEY,
    course_id TEXT NOT NULL,
    title TEXT NOT NULL,
    submission_type TEXT,
    due_at TIMESTAMP,
    first_detected_missing TIMESTAMP,
    status TEXT CHECK(status IN ('GRACE_PERIOD', 'RESOLVED', 'SUPPRESSED', 'ALERT_DISPATCHED')),
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Alert deduplication ledger
CREATE TABLE IF NOT EXISTS alert_ledger (
    event_id TEXT PRIMARY KEY,
    event_type TEXT NOT NULL, -- 'MISSING_WORK_POST_GRACE', 'CONFIRMED_MISSING', 'GRADE_DROP'
    dispatched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    payload_json TEXT
);
```

---

## 4. Module Specifications

### 4.1 Configuration Loader (`bellmon/config.py`)
- Reads configuration from `config.toml` or environment variables using Pydantic Settings.
- Configuration parameters:
  - `CANVAS_BASE_URL`, `CANVAS_API_TOKEN`
  - `POWERSCHOOL_BASE_URL`, `POWERSCHOOL_USERNAME`, `POWERSCHOOL_PASSWORD`
  - `PUSH_SERVICE` (`pushover` or `ntfy`), `PUSHOVER_USER_KEY`, `NTFY_TOPIC_URL`
  - `GRACE_PERIOD_HOURS` (Default: 36)
  - `GRADE_DROP_THRESHOLD` (Default: 4.0)

### 4.2 Harvesters (`bellmon/harvesters/`)
- **Canvas Harvester (`canvas.py`)**: Fetches missing submissions via `/api/v1/users/self/missing_submissions` and course assignments.
- **PowerSchool Harvester (`powerschool.py`)**: Fetches course grade percentages, assignment marks, and status flags.

### 4.3 Heuristics & Rules Engine (`bellmon/engine/`)
- **Missing Work Matrix (`missing_work.py`)**:
  - Implements state transition table.
  - If Canvas missing & PS blank $\to$ status `GRACE_PERIOD`.
  - If status `GRACE_PERIOD` and `elapsed_hours >= 36` $\to$ queue alert & status `ALERT_DISPATCHED`.
  - If Canvas missing & PS score $>0$ or `isCollected` $\to$ status `SUPPRESSED`.
  - If PS `isMissing: true` or `score: 0` $\to$ bypass grace period, status `ALERT_DISPATCHED`.
- **Grade Trajectory Evaluator (`trajectory.py`)**:
  - Fetches snapshot from 7 days ago (`t-7`) and current percentage (`t-0`).
  - If `(percentage_t7 - percentage_t0) >= 4.0`:
    - Queries recent assignments in that 7-day window.
    - Isolates assignment with max impact: `max(points_possible - points_earned)`.
    - Formats velocity drop alert.

### 4.4 Push Notification Router (`bellmon/notifications/push.py`)
- Formats P0 alert payload.
- Dispatches via Pushover API or NTFY HTTP POST.
- Writes `event_id` to `alert_ledger` table.

---

## 5. Implementation Task Hierarchy

1. **Task 1: Core Scaffolding & Configuration** (`config.py`, `config.example.toml`, `requirements.txt`)
2. **Task 2: State Store & Database Layer** (`storage/db.py`, migrations)
3. **Task 3: Harvester Clients** (`harvesters/canvas.py`, `harvesters/powerschool.py`)
4. **Task 4: Rules Engine & Heuristics** (`engine/missing_work.py`, `engine/trajectory.py`)
5. **Task 5: Push Router & Deduplication** (`notifications/push.py`)
6. **Task 6: CLI Runner & Pipeline Integration** (`cli.py`)
7. **Task 7: Test Suite & Verification** (`tests/`)
