# Tasks: Phase 1.2 Asymmetric System Authority & 36-Hour Grace Period Evaluation Engine

## Task Overview

- Total Tasks: 8
- Target Feature Branch: `007-phase-1-2-asymmetric-authority-grace-period`

---

## Phase 1: Engine Data Models & Enums

- [x] **Task 1: Define Enums & Input/Output Alert Models** (`src/engine/models.py`)
  - Define `AssignmentStatus` enum (`NEW`, `GRACE_PERIOD`, `EXPIRED`, `CONFIRMED_MISSING`, `RESOLVED`, `SUPPRESSED`).
  - Define `AlertSource` enum (`CANVAS_GRACE_EXPIRED`, `POWERSCHOOL_CONFIRMED`).
  - Define Pydantic models `CanvasAssignmentInput`, `PowerSchoolAssignmentInput`, and `PendingMissingAlert`.

- [x] **Task 2: Export Engine Models** (`src/engine/__init__.py`)
  - Export `AssignmentStatus`, `AlertSource`, `CanvasAssignmentInput`, `PowerSchoolAssignmentInput`, `PendingMissingAlert`.

---

## Phase 2: Core Authority & Grace Period Engine

- [x] **Task 3: Implement Weekend-Aware Elapsed Hour Calculator** (`src/engine/authority.py`)
  - Implement `calculate_weekday_elapsed_hours(start_dt: datetime, end_dt: datetime, timezone_str: str = "America/Los_Angeles") -> float`.
  - Ensure Friday 17:00:00 to Monday 08:00:00 blackout hours consume 0 hours of grace period budget.

- [x] **Task 4: Implement Canvas Assignment Grace & Suppression Logic** (`src/engine/authority.py`)
  - Implement `evaluate_canvas_assignment()` in `AsymmetricAuthorityEngine`.
  - Handle `GRACE_PERIOD` initialization for `online_upload`.
  - Handle `SUPPRESSED` status for `on_paper` / `none` submission types.
  - Handle `EXPIRED` transition & alert generation after 36 weekday hours.
  - Handle `RESOLVED` transition when `is_missing` becomes `False`.

- [x] **Task 5: Implement PowerSchool Direct Alert Trigger Logic** (`src/engine/authority.py`)
  - Implement `evaluate_powerschool_assignment()` in `AsymmetricAuthorityEngine`.
  - Mark `isMissing: true` or `score: 0` immediately as `CONFIRMED_MISSING` and generate a `POWERSCHOOL_CONFIRMED` alert payload.

---

## Phase 3: Unit Testing & Verification

- [x] **Task 6: Create Unit Test Suite for Authority Engine** (`tests/test_authority.py`)
  - Write test cases for weekend window pausing (e.g. Friday 5 PM through Monday 8 AM).
  - Write test cases for Canvas digital grace initialization, expiration, resolution, and suppression.
  - Write test cases for PowerSchool confirmed missing direct alert triggers.

- [x] **Task 7: Execute Pytest Suite & Code Quality Checks**
  - Run `pytest tests/test_authority.py` and verify 100% pass rate.
  - Ensure zero regressions in `tests/test_firestore.py`.

---

## Phase 4: Batch Runner Integration & Spec Verification

- [x] **Task 8: Wire Engine into Main / Storage Integration & Update Documentation** (`src/main.py`, `specs/STATUS.md`)
  - Update `src/main.py` if needed or ensure `AsymmetricAuthorityEngine` is accessible for batch pipelines.
  - Update `specs/STATUS.md` reflecting Feature 007 status as 100% completed.
