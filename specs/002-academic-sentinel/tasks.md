# Tasks: Academic & Workload Sentinel

**Input**: Design documents from `/specs/002-academic-sentinel/`  
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/  

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Explicit file paths included in all descriptions.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization, environment, and base layout

- [x] T001 Create project package directory structure per implementation plan (`src/harvesters/`, `src/engine/`, `src/storage/`, `src/router/`, `src/cli/`, `terraform/`, `.github/workflows/`, `tests/`)
- [x] T002 Initialize Python 3.11 environment with dependencies (`httpx`, `jinja2`, `google-cloud-firestore`, `pytest`) in `requirements.txt`
- [x] T003 [P] Configure environment variable loading and settings module in `src/config.py`
- [x] T028 [P] Define Terraform infrastructure (Cloud Run, Cloud Scheduler, Firestore, IAM) in `terraform/main.tf`, `terraform/variables.tf`, `terraform/scheduler.tf`, and `terraform/outputs.tf`
- [x] T029 [P] Create GitHub Actions Guardian plan workflow in `.github/workflows/guardian-plan.yml`
- [x] T030 [P] Create GitHub Actions Guardian apply workflow in `.github/workflows/guardian-apply.yml`


---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Harvester bases, data models, state storage, and idempotency ledger

- [x] T004 Implement student and course data entities in `src/storage/models.py`
- [x] T005 [P] Implement Firestore state store client and atomic snapshot updater in `src/storage/firestore.py`
- [x] T006 [P] Implement alert ledger idempotency tracker in `src/storage/ledger.py`
- [x] T007 Implement Canvas REST client harvester in `src/harvesters/canvas.py`
- [x] T008 Implement PowerSchool REST client harvester in `src/harvesters/powerschool.py`
- [x] T009 [P] Implement P0 Push notification router (Pushover / NTFY) in `src/router/push.py`

---

## Phase 3: User Story 1 - Digital Missing Assignment Grace Period (Priority: P1) 🎯 MVP

**Goal**: Apply a 36-hour grace period buffer before notifying parents of overdue digital upload assignments.

**Independent Test**: Simulate an overdue Canvas `online_upload` assignment without PowerSchool score; verify state is set to `GRACE_PERIOD`, resolves silently if turned in within 36 hours, and fires P0 alert post-36h.

- [x] T010 [P] [US1] Unit test for grace period calculation and status transitions in `tests/unit/test_grace_period.py`
- [x] T011 [US1] Implement 36-hour grace period state evaluator in `src/engine/grace_period.py`
- [x] T012 [US1] Integrate grace period evaluator into main sync runner in `src/cli/sync.py`

---

## Phase 4: User Story 2 - Confirmed Missing Work Direct Alerting (Priority: P1)

**Goal**: Instantly dispatch P0 push alerts for assignments explicitly marked as missing or 0 in PowerSchool, bypassing grace periods.

**Independent Test**: Supply PowerSchool status `isMissing: true` or `score: 0`; verify grace period is bypassed and immediate push alert is dispatched.

- [x] T013 [P] [US2] Unit test for confirmed missing work rule in `tests/unit/test_confirmed_missing.py`
- [x] T014 [US2] Implement confirmed missing work evaluator in `src/engine/missing_work.py`
- [x] T015 [US2] Wire confirmed missing evaluator to push router in `src/engine/evaluator.py`

---

## Phase 5: User Story 3 - Paper & In-Class Work False-Positive Suppression (Priority: P1)

**Goal**: Suppress Canvas missing notifications when work is collected or graded in PowerSchool.

**Independent Test**: Set Canvas `missing: true` and PowerSchool `score > 0` or `isCollected: true`; verify alert is suppressed and logged as `SUPPRESSED_PAPER_OR_GRADED`.

- [x] T016 [P] [US3] Unit test for paper suppression matrix in `tests/unit/test_paper_suppression.py`
- [x] T017 [US3] Implement paper/graded suppression logic in `src/engine/missing_work.py`

---

## Phase 6: User Story 4 - Significant Grade Trajectory Drop Warning (Priority: P1)

**Goal**: Track rolling 7-day course grade velocity and fire P0 push alert when grade drops by $\ge 4.0\%$.

**Independent Test**: Supply a grade snapshot sequence showing a 5.0% drop over 7 days; verify system isolates the impacting assignment and dispatches drop alert.

- [x] T018 [P] [US4] Unit test for 7-day rolling grade velocity drop calculator in `tests/unit/test_velocity_drop.py`
- [x] T019 [US4] Implement velocity drop evaluator and impacting assignment isolator in `src/engine/velocity.py`

---

## Phase 7: User Story 5 - Sunday Night Workload & Planning Digest (Priority: P2)

**Goal**: Generate and send HTML email digest every Sunday at 6:00 PM highlighting workload clumping ($\ge 2$ major assessments in 48h).

**Independent Test**: Trigger Sunday digest builder with 2 major exams due within 48 hours; verify Jinja2 HTML email output with workload warning banner.

- [x] T020 [P] [US5] Implement Jinja2 HTML email digest template in `src/router/templates/sunday_digest.html`
- [x] T021 [P] [US5] Implement workload clumping radar scanner in `src/engine/clumping.py`
- [x] T022 [US5] Implement email digest generator and SMTP router in `src/router/email.py`

---

## Phase 8: User Story 6 - Attendance Anomaly Detection (Priority: P3)

**Goal**: Dispatch daily P0 push alerts for unexcused attendance codes (`A`, `T`, `U`, `CUT`).

**Independent Test**: Supply period attendance code `T`; verify P0 alert dispatch for tardy anomaly.

- [x] T023 [P] [US6] Unit test for attendance code filter in `tests/unit/test_attendance.py`
- [x] T024 [US6] Implement attendance anomaly evaluator in `src/engine/attendance.py`

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: End-to-end integration, CLI entry point, contract validation, and documentation updates.

- [x] T025 Implement CLI command-line runner in `src/cli/sync.py`
- [x] T026 [P] Add contract validation tests for sync JSON schema in `tests/contract/test_sync_schema.py`
- [x] T027 Run quickstart validation script and verify test coverage in `tests/integration/test_end_to_end.py`


---

## Dependencies & Execution Order

```
[Phase 1: Setup] ──> [Phase 2: Foundational] ──┬──> [Phase 3: US1 (Grace Period)]
                                              ├──> [Phase 4: US2 (Confirmed Missing)]
                                              ├──> [Phase 5: US3 (Paper Suppression)]
                                              ├──> [Phase 6: US4 (Velocity Drop)]
                                              ├──> [Phase 7: US5 (Sunday Digest)]
                                              └──> [Phase 8: US6 (Attendance)]
                                                                  │
                                                                  ▼
                                                      [Phase 9: Polish & E2E]
```
