# Tasks: Phase 1.1 GCP Cloud Firestore Student State Persistence Engine

**Input**: Design documents from `/specs/006-phase-1-1-firestore-state-engine/`  
**Prerequisites**: [plan.md](./plan.md), [spec.md](./spec.md), [data-model.md](./data-model.md), [contracts/storage_engine_interface.md](./contracts/storage_engine_interface.md)

---

## Format: `- [ ] [ID] [P?] [Story?] Description with file path`

- **[P]**: Can run in parallel (different files, no direct dependencies)
- **[Story]**: Which user story this task belongs to (`[US1]`, `[US2]`, `[US3]`)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Storage module initialization and structure

- [ ] T001 Initialize storage package structure in `src/storage/__init__.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core data models that ALL storage operations depend on

**⚠️ CRITICAL**: No user story storage operations can be implemented until data models are defined.

- [ ] T002 Define Pydantic v2 state models (`GradeSnapshot`, `CourseState`, `TrackedAssignment`, `AttendanceEvent`, `SessionCookies`, `StudentState`) in `src/storage/models.py`

**Checkpoint**: Foundation ready — user story implementation can begin.

---

## Phase 3: User Story 1 - Student State Document Store (Priority: P1) 🎯 MVP

**Goal**: Load and store student academic state documents in GCP Cloud Firestore at `students/{student_id}` with clean default fallback.

**Independent Test**: Running `pytest tests/test_firestore.py` verifies reading, updating, and initializing default student state documents against `MockFirestoreClient`.

### Implementation for User Story 1

- [ ] T003 [P] [US1] Implement `MockFirestoreClient` in-memory document/collection reference simulator in `src/storage/firestore.py`
- [ ] T004 [US1] Implement `FirestoreStateEngine` class with `get_student_state` and `update_student_state` methods in `src/storage/firestore.py`
- [ ] T005 [P] [US1] Write unit tests for student state document read/write and default initialization in `tests/test_firestore.py`

**Checkpoint**: User Story 1 complete and independently testable via pytest.

---

## Phase 4: User Story 2 - Grade History Snapshot Ledger (Priority: P1)

**Goal**: Append dated grade snapshots to `courses.{course_id}.history` and query historical snapshots for $[t-10, t-7]$ date window comparisons.

**Independent Test**: Appending daily grade snapshots adds entries without overwriting existing history, and querying historical window returns nearest matching snapshot.

### Implementation for User Story 2

- [ ] T006 [US2] Implement `append_grade_snapshot` and `get_grade_history` methods in `FirestoreStateEngine` (`src/storage/firestore.py`)
- [ ] T007 [P] [US2] Write unit tests for grade history snapshot appending and date window queries in `tests/test_firestore.py`

**Checkpoint**: User Story 2 complete and independently testable via pytest.

---

## Phase 5: User Story 3 - Session Cookie Storage & Retrieval (Priority: P2)

**Goal**: Store and retrieve encrypted SAML session cookies in Firestore under `students/{student_id}.session_cookies` for Playwright scraper session reuse.

**Independent Test**: Saving session cookies updates `session_cookies.psaid` and `session_cookies.updated_at`; retrieving returns the parsed `SessionCookies` model or `None`.

### Implementation for User Story 3

- [ ] T008 [US3] Implement `save_session_cookies` and `get_session_cookies` methods in `FirestoreStateEngine` (`src/storage/firestore.py`)
- [ ] T009 [P] [US3] Write unit tests for session cookie persistence and retrieval in `tests/test_firestore.py`

**Checkpoint**: All user stories complete and independently functional.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Package exports, integration verification, and execution validation

- [ ] T010 Export `FirestoreStateEngine` and data models from `src/storage/__init__.py`
- [ ] T011 [P] Verify execution of tests and quickstart guide in `specs/006-phase-1-1-firestore-state-engine/quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Can start immediately.
- **Foundational (Phase 2)**: Depends on Setup (T001). Blocks all User Stories.
- **User Story 1 (Phase 3)**: Depends on Foundational (T002).
- **User Story 2 (Phase 4)**: Depends on User Story 1 (T004).
- **User Story 3 (Phase 5)**: Depends on User Story 1 (T004).
- **Polish (Phase 6)**: Depends on completion of all User Stories (T003-T009).

### Sequential Task Execution Order

1. `T001` → `T002` (Models)
2. `T003` (Mock Client) + `T004` (Engine Core) → `T005` (US1 Tests)
3. `T006` (Grade History) → `T007` (US2 Tests)
4. `T008` (Cookies) → `T009` (US3 Tests)
5. `T010` (Export) + `T011` (Quickstart validation)

---

## Implementation Strategy

### MVP Scope (User Story 1 Only)
1. Complete Phase 1 & Phase 2 (Infrastructure & Data Models).
2. Complete Phase 3 (Student State Document Store).
3. Validate User Story 1 via `pytest tests/test_firestore.py`.

### Incremental Delivery
- Add Grade History Ledger (User Story 2).
- Add Session Cookie Storage (User Story 3).
- Run full test suite (`pytest`) to guarantee 100% pass rate.
