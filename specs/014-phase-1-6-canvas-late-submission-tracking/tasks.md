# Tasks: Phase 1.6 Canvas Late Submission Tracking

**Feature**: `014-phase-1-6-canvas-late-submission-tracking`  
**Status**: Ready for Implementation  

## Tasks

- [ ] **Task 1: Add `LateSubmissionRecord` data model**
  - **File**: `src/storage/models.py`
  - **Description**: Add `LateSubmissionRecord` Pydantic v2 model with fields `assignment_id`, `course_id`, `course_name`, `title`, `due_at`, `submitted_at`, `minutes_late`, `detected_at`, and `is_late`.
  - **Verification**: `python -c "from src.storage.models import LateSubmissionRecord; print(LateSubmissionRecord.model_json_schema())"`

- [ ] **Task 2: Implement Firestore storage & querying for late submission ledger**
  - **File**: `src/storage/firestore.py`
  - **Description**: Add support for subcollection `students/{student_id}/late_submissions/{assignment_id}` in `MockFirestoreClient` and `FirestoreStateEngine`. Implement methods `save_late_submission`, `save_late_submissions`, and `get_late_submissions(student_id, start_date, end_date)`.
  - **Verification**: Run Firestore storage unit tests.

- [ ] **Task 3: Extend Canvas REST API ingestion for late submissions**
  - **File**: `src/ingestion/canvas.py`
  - **Description**: Add `CanvasSubmission` data model and `get_student_submissions` / `process_late_submissions` methods in `CanvasClient` to ingest submissions, check `late: true` or `submitted_at > due_at`, compute `minutes_late`, and generate `LateSubmissionRecord` list. Handle edge cases (missing `submitted_at`, updated due dates).
  - **Verification**: Run ingestion unit tests with mock Canvas responses.

- [ ] **Task 4: Add unit and integration tests**
  - **File**: `tests/test_canvas_late_submissions.py`
  - **Description**: Create test suite covering FR-001 through FR-006, deduplication, late duration computation, edge cases (due date updates, missing submission timestamp), and date range queries.
  - **Verification**: `pytest tests/test_canvas_late_submissions.py -v`

- [ ] **Task 5: Update Speckit Status Dashboard**
  - **File**: `specs/STATUS.md`
  - **Description**: Update feature `014` status to Complete in `specs/STATUS.md`.
  - **Verification**: Check `specs/STATUS.md`.
