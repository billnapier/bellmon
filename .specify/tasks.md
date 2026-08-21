# Task Breakdown: Bellmon MVP - Core Academic Sentinel & Noise Reduction

**Feature**: Core Academic Sentinel & Noise Reduction  
**Specification**: [.specify/spec.md](../.specify/spec.md)  
**Implementation Plan**: [.specify/plan.md](../.specify/plan.md)  

---

## Dependency Graph & Execution Order

```
Phase 1: Setup (T001 - T003)
       │
       ▼
Phase 2: Foundational Storage & Models (T004 - T005)
       │
       ▼
Phase 3: Harvester Clients [US1] (T006 - T007)
       │
       ▼
Phase 4: Missing Work Matrix & 36h Grace [US2] (T008)
       │
       ▼
Phase 5: Grade Velocity Drop Evaluator [US3] (T009)
       │
       ▼
Phase 6: Push Router & Deduplication Ledger [US4] (T010)
       │
       ▼
Phase 7: CLI Runner & Pipeline Orchestrator [US5] (T011 - T012)
```

---

## Phase 1: Setup & Project Initialization

- [ ] T001 Initialize Python project directory structure and dependencies in `requirements.txt`
- [ ] T002 Create sample configuration template in `config.example.toml`
- [ ] T003 [P] Implement configuration loader and settings validator in `bellmon/config.py`

---

## Phase 2: Foundational Storage & Data Models

- [ ] T004 Implement SQLite database schema and connection manager in `bellmon/storage/db.py`
- [ ] T005 [P] Define unified Pydantic data structures for Courses, Assignments, and Snapshots in `bellmon/engine/models.py`

---

## Phase 3: User Story 1 - API Harvester Clients [US1]

**Goal**: Ingest current course percentages, assignment states, and missing flags from Canvas LMS and PowerSchool SIS.

- [ ] T006 [P] [US1] Implement Canvas REST API harvester client in `bellmon/harvesters/canvas.py`
- [ ] T007 [P] [US1] Implement PowerSchool API harvester client in `bellmon/harvesters/powerschool.py`

---

## Phase 4: User Story 2 - Cross-System Missing Work & Grace Period [US2]

**Goal**: Cross-reference missing items, suppress paper submissions, and enforce a 36-hour grace period buffer on digital uploads.

- [ ] T008 [US2] Implement Cross-System Missing Work Resolution Matrix and 36-hour grace period evaluator in `bellmon/engine/missing_work.py`

---

## Phase 5: User Story 3 - Grade Trajectory Velocity Drop Evaluator [US3]

**Goal**: Monitor rolling 7-day course grade snapshots and trigger warnings on drops $\ge 4.0\%$.

- [ ] T009 [US3] Implement 7-day rolling grade velocity drop evaluator and impacting item isolator in `bellmon/engine/trajectory.py`

---

## Phase 6: User Story 4 - Push Notification Router & Deduplication [US4]

**Goal**: Format P0 notification payloads and dispatch via Pushover / NTFY while enforcing alert deduplication.

- [ ] T010 [US4] Implement Pushover and NTFY push dispatchers and deduplication ledger in `bellmon/notifications/push.py`

---

## Phase 7: User Story 5 - CLI Runner & Pipeline Orchestrator [US5]

**Goal**: Unify all modules into a single CLI command (`bellmon sync`) for scheduled execution.

- [ ] T011 [US5] Implement CLI entry point and pipeline orchestrator in `bellmon/cli.py`
- [ ] T012 [P] [US5] Create unit test suite for rules engine and state store in `tests/test_engine.py`

---

## Parallel Execution Opportunities

- **Phase 1**: T003 can be built in parallel with T001/T002.
- **Phase 2**: T005 (Pydantic models) can be built in parallel with T004 (DB schema).
- **Phase 3**: T006 (Canvas client) and T007 (PowerSchool client) can be implemented completely independently in parallel.
- **Phase 7**: T012 (Tests) can be executed alongside T011 (CLI wrapper).
