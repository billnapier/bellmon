# Implementation Plan: Phase 1.2 Asymmetric System Authority & 36-Hour Grace Period Evaluation Engine

**Branch**: `007-phase-1-2-asymmetric-authority-grace-period` | **Date**: 2026-08-24 | **Spec**: [spec.md](./spec.md)  
**Input**: Feature specification from `/specs/007-phase-1-2-asymmetric-authority-grace-period/spec.md`

## Summary

Implement the `AsymmetricAuthorityEngine` in `src/engine/authority.py` to evaluate student assignment missing statuses from Canvas and PowerSchool independently. The engine calculates a 36-hour grace period timer for digital Canvas missing assignments (`online_upload`) excluding weekend hours (Friday 17:00 to Monday 08:00), suppresses non-digital Canvas assignments (`on_paper`, `none`), and immediately triggers confirmed missing alerts for PowerSchool assignments marked `isMissing: true` or `score: 0`.

## Technical Context

**Language/Version**: Python 3.12  
**Primary Dependencies**: `pydantic` (v2), `datetime`, `zoneinfo`, `pytest`  
**Storage Integration**: `FirestoreStateEngine` (`src/storage/firestore.py`) & Pydantic models (`src/storage/models.py`)  
**Testing**: `pytest` (Isolated unit & integration tests)  
**Target Platform**: Linux container (Cloud Run batch execution runtime)  
**Project Type**: Single Python Application / Service  
**Performance Goals**: Fast batch processing of assignment statuses (< 100ms per evaluation run per student)  
**Constraints**: Pure asymmetric model (no fuzzy cross-system title matching between Canvas and PowerSchool); zero hardcoded credentials or fake placeholders.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] **Principle 1 (Single Environment / Test-in-Prod)**: Tests execute via `pytest` offline/in-memory.
- [x] **Principle 2 (Zero-Trust Secrets)**: No secrets required for pure logic engine.
- [x] **Principle 3 (Asymmetric System Authority)**: Canvas digital upload assignments use 36h grace period; PowerSchool missing/zero scores immediately confirm missing; Canvas paper/none suppressed.
- [x] **Principle 4 (Zero Fake Placeholders & Dynamic Querying)**: Real business logic for weekend pausing and status transitions.
- [x] **Principle 5 (PR-Only Enforcement & Mandatory CI Testing)**: Implemented on feature branch `007-phase-1-2-asymmetric-authority-grace-period`.
- [x] **Principle 6 (Open-Source First)**: Built using standard Python library (`datetime`, `zoneinfo`) and `pydantic`.
- [x] **Principle 7 (Automated Container CI/CD)**: Handled seamlessly via main branch PR merge.

## Project Structure

### Documentation (this feature)

```text
specs/007-phase-1-2-asymmetric-authority-grace-period/
├── spec.md              # Feature specification
├── plan.md              # Implementation plan (this file)
├── research.md          # Phase 0 research output (weekend calculation logic, status transitions)
├── data-model.md        # Phase 1 output (Enum definitions, PendingMissingAlert schema)
├── quickstart.md        # Phase 1 output (Unit test execution guide)
└── contracts/           # Phase 1 output
    └── authority_engine_interface.md # Python engine interface contract
```

### Source Code Layout

```text
src/
├── engine/
│   ├── __init__.py
│   └── authority.py     # AsymmetricAuthorityEngine & grace period calculator
├── storage/
│   ├── models.py        # Updated Pydantic models (AssignmentStatus, PendingMissingAlert, etc.)
│   └── firestore.py
└── main.py              # Batch runner integration

tests/
├── test_authority.py   # Authority engine & weekend grace period unit tests
└── test_firestore.py
```

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|---|---|---|
| None | N/A | N/A |
