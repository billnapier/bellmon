# Implementation Tasks: Phase 3.1 Customizable Notification Thresholds and Grace Periods

## Phase 1: Data Models & Storage Infrastructure
- [ ] Task 1: Extend `src/storage/models.py` with `StudentPreferences` model and embed it into `StudentSnapshot`.
- [ ] Task 2: Update `src/storage/firestore.py` to support `update_student_preferences` and preference deserialization.

## Phase 2: Engine Overrides & Dynamic Logic
- [ ] Task 3: Update `src/engine/authority.py` to accept and evaluate custom `StudentPreferences` (grace period hours & weekend pause).
- [ ] Task 4: Update `src/engine/velocity.py` to accept and evaluate custom `StudentPreferences` (grade drop threshold).
- [ ] Task 5: Update `src/engine/late_submissions.py` to accept and evaluate custom `StudentPreferences` (late submission threshold).
- [ ] Task 6: Update `src/radar/engine.py` to accept and evaluate custom `StudentPreferences` (workload clumping count & window hours).
- [ ] Task 7: Wire `student.preferences` in `src/main.py` when executing batch sentinel passes.

## Phase 3: Verification & Integration Testing
- [ ] Task 8: Implement unit and integration tests in `tests/test_custom_preferences.py` and ensure 100% test suite pass.
