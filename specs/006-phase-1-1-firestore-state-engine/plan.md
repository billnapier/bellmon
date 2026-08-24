# Implementation Plan: Phase 1.1 GCP Cloud Firestore Student State Persistence Engine

**Branch**: `006-phase-1-1-firestore-state-engine` | **Date**: 2026-08-24 | **Spec**: [spec.md](./spec.md)  
**Input**: Feature specification from `/specs/006-phase-1-1-firestore-state-engine/spec.md`

## Summary

Implement a thread-safe, resilient GCP Cloud Firestore state persistence wrapper (`FirestoreStateEngine`) and Pydantic v2 data models (`StudentState`, `CourseState`, `TrackedAssignment`, `AttendanceEvent`, `SessionCookies`) in `src/storage/`. This layer provides stateful tracking across sub-daily batch runs for grace period calculations, grade velocity tracking, attendance deduplication, and SAML session reuse, with an in-memory mock client mode for 100% offline unit test execution (`pytest`).

## Technical Context

**Language/Version**: Python 3.12  
**Primary Dependencies**: `google-cloud-firestore`, `pydantic` (v2), `pytest`  
**Storage**: GCP Cloud Firestore (Native Mode at `students/{student_id}`)  
**Testing**: `pytest` (Isolated in-memory mock storage mode)  
**Target Platform**: Linux container (Cloud Run batch execution runtime)  
**Project Type**: Single Python Application / Service  
**Performance Goals**: Read and write operations complete within 200ms per student record (SC-001)  
**Constraints**: Zero hardcoded credentials or fake placeholders (Principle 4); offline test execution without GCP network calls (Principle 1 & Principle 5)  
**Scale/Scope**: 1 student document per student ID, containing courses, tracked assignments, attendance events, and grade history snapshots  

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] **Principle 1 (Single Environment / Test-in-Prod)**: No staging environment. Local testing uses in-memory mock client via `pytest`.
- [x] **Principle 2 (Zero-Trust Secrets)**: Session cookies encrypted; GCP IAM used for Firestore authentication in Cloud Run.
- [x] **Principle 3 (Asymmetric System Authority)**: Models separate PowerSchool course history/attendance from Canvas assignment tracking.
- [x] **Principle 4 (Zero Fake Placeholders & Dynamic Querying)**: All commands dynamically query active GCP project via `gcloud config get-value project`.
- [x] **Principle 5 (PR-Only Enforcement & Mandatory CI Testing)**: Implemented on dedicated feature branch `006-phase-1-1-firestore-state-engine`. CI executes unit tests on PR.
- [x] **Principle 6 (Open-Source First)**: Uses official `google-cloud-firestore` SDK and standard `pydantic` models.
- [x] **Principle 7 (Automated Container CI/CD)**: Handled seamlessly via main branch PR merge.

## Project Structure

### Documentation (this feature)

```text
specs/006-phase-1-1-firestore-state-engine/
├── spec.md              # Feature specification
├── plan.md              # Implementation plan (this file)
├── research.md          # Phase 0 output (Storage SDK, mocking strategy, Pydantic models)
├── data-model.md        # Phase 1 output (Entity schemas & field specs)
├── quickstart.md        # Phase 1 output (Offline unit test & setup guide)
└── contracts/           # Phase 1 output
    └── storage_engine_interface.md # Python interface protocol & contract
```

### Source Code Layout

```text
src/
├── storage/
│   ├── __init__.py
│   ├── models.py        # Pydantic v2 state schemas (StudentState, CourseState, etc.)
│   └── firestore.py     # FirestoreStateEngine & MockFirestoreClient implementations
├── ingestion/
│   ├── canvas.py
│   └── powerschool.py
└── main.py

tests/
├── test_firestore.py    # Storage engine & model unit test suite
├── test_canvas.py
├── test_powerschool.py
└── test_main.py
```

**Structure Decision**: Single Python project structure with modular `src/storage/` package.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|---|---|---|
| None | N/A | N/A |
