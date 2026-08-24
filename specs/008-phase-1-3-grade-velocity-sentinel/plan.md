# Implementation Plan: Phase 1.3 Grade Velocity Drop ($\ge 4.0\%$) Sentinel & Silent Warming Tracker

**Branch**: `008-phase-1-3-grade-velocity-sentinel` | **Date**: 2026-08-24 | **Spec**: [spec.md](./spec.md)  
**Input**: Feature specification from `/specs/008-phase-1-3-grade-velocity-sentinel/spec.md`

## Summary

Implement the `GradeVelocityEngine` in `src/engine/velocity.py` to evaluate student academic course grade drops of $\ge 4.0\%$ against historical baseline snapshots within a $[t-10, t-7]$ day window. The engine enforces early-term noise suppression (suppressing alerts when course graded points $< 100$ AND term active duration $< 21$ calendar days) and a 7-day silent warming protocol for new student profile baselines.

## Technical Context

**Language/Version**: Python 3.12  
**Primary Dependencies**: `pydantic` (v2), `datetime`, `pytest`  
**Storage Integration**: Grade history snapshots from `CourseState.history` (`src/storage/models.py`)  
**Testing**: `pytest` (Isolated unit & integration tests)  
**Target Platform**: Linux container (Cloud Run batch execution runtime)  
**Performance Goals**: Fast batch evaluation (< 50ms per student profile)  
**Constraints**: Zero false alerts during 7-day warming; 100% noise suppression during early-term low-point assignments.

## Constitution Check

- [x] **Principle 1 (Single Environment / Test-in-Prod)**: Offline pytest unit test verification.
- [x] **Principle 2 (Zero-Trust Secrets)**: No secrets required for pure calculation logic.
- [x] **Principle 3 (Asymmetric System Authority)**: Integrates seamlessly with asymmetric authority alert processing.
- [x] **Principle 4 (Zero Fake Placeholders)**: Real datetime calculations and delta math.
- [x] **Principle 5 (PR-Only Enforcement & Mandatory CI Testing)**: Executed on feature branch `008-phase-1-3-grade-velocity-sentinel`.
- [x] **Principle 6 (Open-Source First)**: Standard library and Pydantic.
- [x] **Principle 7 (Automated Container CI/CD)**: Handled via GitHub Actions pipeline on PR merge.

## Project Structure

### Documentation (this feature)

```text
specs/008-phase-1-3-grade-velocity-sentinel/
├── spec.md              # Feature specification
├── plan.md              # Implementation plan (this file)
├── research.md          # Research output (snapshot selection, delta math, suppression matrix)
├── data-model.md        # Data models (PendingGradeDropAlert, CourseVelocityInput, StudentVelocityContext)
├── quickstart.md        # Quickstart & test execution guide
└── contracts/
    └── velocity_engine_interface.md # Python engine interface contract
```

### Source Code Layout

```text
src/
├── engine/
│   ├── __init__.py
│   ├── models.py        # Updated Pydantic models for Grade Velocity
│   └── velocity.py      # GradeVelocityEngine implementation
├── storage/
│   └── models.py        # Existing storage schemas
└── main.py              # Batch runner integration

tests/
├── test_velocity.py     # Unit test suite for velocity drop detection
└── test_authority.py
```

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|---|---|---|
| None | N/A | N/A |
