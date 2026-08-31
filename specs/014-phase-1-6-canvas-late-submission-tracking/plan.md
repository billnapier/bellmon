# Implementation Plan: Phase 1.6 Canvas Late Submission Tracking

**Feature Branch**: `014-phase-1-6-canvas-late-submission-tracking`  
**Created**: 2026-08-31  
**Status**: In Planning  

## Technical Context

- **Language / Framework**: Python 3.11+, Pydantic v2
- **Data Persistence**: GCP Cloud Firestore (`students/{student_id}/late_submissions/{assignment_id}`)
- **External Integration**: Canvas LMS REST API (submissions endpoint `/api/v1/students/{student_id}/submissions` or course submissions)
- **Key Modules**:
  - `src/ingestion/canvas.py`: Ingestion client extension for Canvas submission parsing & late detection.
  - `src/storage/models.py`: Pydantic data model `LateSubmissionRecord`.
  - `src/storage/firestore.py`: Firestore storage operations for `late_submissions` ledger.

## Constitution Check

- **Principle 1 (Data Minimization)**: Storing only required assignment metadata, submission timestamps, and calculated late minutes.
- **Principle 4 (Idempotency)**: Firestore updates use deterministic document IDs (`assignment_id`) under `students/{student_id}/late_submissions/`.
- **Principle 6 (No Unofficial Scrapers for Canvas)**: Using standard REST API calls and observer/student submission data structures.

## Planning Artifacts

- **Research**: `specs/014-phase-1-6-canvas-late-submission-tracking/research.md`
- **Data Model**: `specs/014-phase-1-6-canvas-late-submission-tracking/data-model.md`
- **Quickstart**: `specs/014-phase-1-6-canvas-late-submission-tracking/quickstart.md`
