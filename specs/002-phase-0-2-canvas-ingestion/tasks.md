# Tasks: Phase 0.2 Canvas LMS REST API Ingestion Module

**Input**: Design documents from `/specs/002-phase-0-2-canvas-ingestion/`

## Phase 1: Ingestion Module Setup

- [x] T001 Create ingestion package `src/ingestion/__init__.py`
- [x] T002 Implement Canvas data models (`CanvasAssignment`, `CanvasCourse`) in `src/ingestion/canvas.py`

## Phase 2: Core Ingestion Client Implementation

- [x] T003 Implement secret resolution from GCP Secret Manager / env in `src/ingestion/canvas.py`
- [x] T004 Implement `CanvasClient` REST ingestion methods (`get_courses`, `get_missing_submissions`) in `src/ingestion/canvas.py`
- [x] T005 Implement exponential backoff retry logic for Canvas API requests

## Phase 3: Testing & Polish

- [x] T006 Create unit tests in `tests/test_canvas.py` covering mock API responses, missing submissions parsing, and error handling
- [x] T007 Execute pytest suite and verify 100% test pass rate
