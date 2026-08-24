# Implementation Plan: Phase 1.4 Period Attendance Anomaly Sentinel (P0 Alerting)

**Branch**: `009-phase-1-4-attendance-anomaly-sentinel` | **Date**: 2026-08-24 | **Spec**: [spec.md](./spec.md)  
**Input**: Feature specification from `/specs/009-phase-1-4-attendance-anomaly-sentinel/spec.md`

## Summary

Implement `AttendanceSentinel` in `src/engine/attendance.py` to process period-level attendance records harvested from PowerSchool. The sentinel classifies attendance codes into `P0_URGENT` (`A`, `CUT`), `P1_DIGEST` (`T`, `U`), or `IGNORED` (`P`, `E`, `EX`, `ACT`), deduplicates against existing Firestore attendance ledger history, emits P0 alert payloads for immediate notification, and logs minor events for weekly digest summary.

## Technical Context

**Language/Version**: Python 3.12  
**Primary Dependencies**: `pydantic` (v2), `datetime`, `pytest`  
**Storage Integration**: `AttendanceEvent` records stored in Firestore state engine  
**Testing**: `pytest` (Isolated unit tests in `tests/test_attendance.py`)  
**Target Platform**: Linux container (Cloud Run batch execution runtime)  
**Performance Goals**: Fast evaluation (< 10ms per student record set)  
**Constraints**: 0 duplicate P0 alerts dispatched for already notified events; 100% detection of unexcused absences and cuts.

## Constitution Check

- [x] **Principle 1 (Single Environment / Test-in-Prod)**: Offline pytest unit test verification.
- [x] **Principle 2 (Zero-Trust Secrets)**: No secrets required for pure calculation logic.
- [x] **Principle 3 (Asymmetric System Authority)**: Integrates seamlessly with asymmetric authority alert processing.
- [x] **Principle 4 (Zero Fake Placeholders)**: Real timestamp handling and deduplication key matching.
- [x] **Principle 5 (PR-Only Enforcement & Mandatory CI Testing)**: Executed on feature branch `009-phase-1-4-attendance-anomaly-sentinel`.
- [x] **Principle 6 (Open-Source First)**: Standard library and Pydantic.
- [x] **Principle 7 (Automated Container CI/CD)**: Handled via GitHub Actions pipeline on PR merge.

## Project Structure

### Documentation (this feature)

```text
specs/009-phase-1-4-attendance-anomaly-sentinel/
├── spec.md              # Feature specification
├── plan.md              # Implementation plan (this file)
├── research.md          # Research output (severity matrix, deduplication strategy)
├── data-model.md        # Data models (AttendanceCodeSeverity, PendingAttendanceAlert, etc.)
├── quickstart.md        # Quickstart & test execution guide
└── contracts/
    └── attendance_sentinel_interface.md # Python engine interface contract
```

### Source Code Layout

```text
src/
├── engine/
│   ├── __init__.py
│   ├── models.py        # Updated Pydantic models for Attendance Sentinel
│   ├── velocity.py
│   └── attendance.py    # AttendanceSentinel implementation
└── storage/
    └── models.py        # Storage models updated if necessary

tests/
└── test_attendance.py   # Unit test suite for attendance anomaly detection & deduplication
```

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|---|---|---|
| None | N/A | N/A |
