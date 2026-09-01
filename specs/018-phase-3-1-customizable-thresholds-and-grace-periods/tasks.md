# Implementation Tasks: Phase 3.1 Customizable Notification Thresholds and Grace Periods

## Phase 1: Data Models & Storage Infrastructure
- [x] Task 1: Extend `src/storage/models.py` with `StudentPreferences` model and embed it into `StudentSnapshot`.
- [x] Task 2: Update `src/storage/firestore.py` to support `update_student_preferences` and preference deserialization.

## Phase 2: Engine Overrides & Dynamic Logic
- [x] Task 3: Update `src/engine/authority.py` to accept and evaluate custom `StudentPreferences` (grace period hours & weekend pause).
- [x] Task 4: Update `src/engine/velocity.py` to accept and evaluate custom `StudentPreferences` (grade drop threshold).
- [x] Task 5: Update `src/engine/late_submissions.py` to accept and evaluate custom `StudentPreferences` (late submission threshold).
- [x] Task 6: Update `src/radar/engine.py` to accept and evaluate custom `StudentPreferences` (workload clumping count & window hours).
- [x] Task 7: Wire `student.preferences` in `src/main.py` when executing batch sentinel passes.

## Phase 3: Verification & Integration Testing
- [x] Task 8: Implement unit and integration tests in `tests/test_custom_preferences.py` and ensure 100% test suite pass.

