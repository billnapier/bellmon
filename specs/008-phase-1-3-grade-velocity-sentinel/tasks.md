# Tasks: Phase 1.3 Grade Velocity Drop ($\ge 4.0\%$) Sentinel & Silent Warming Tracker

## Implementation Tasks

### Task Group 1: Data Models & Contracts (User Stories 1-3)
- [x] **Task 1.1**: Define `PendingGradeDropAlert`, `CourseVelocityInput`, and `StudentVelocityContext` Pydantic models in `src/engine/models.py`.
- [x] **Task 1.2**: Export velocity data models in `src/engine/__init__.py`.

### Task Group 2: Core Grade Velocity Engine (User Story 1 - Rolling Drop Detection)
- [x] **Task 2.1**: Create `src/engine/velocity.py` with `GradeVelocityEngine` class skeleton.
- [x] **Task 2.2**: Implement `find_baseline_snapshot()` method to select historical baseline in $[t-10, t-7]$ day window (with $[t-14, t-7]$ fallback).
- [x] **Task 2.3**: Implement grade drop delta calculation $\Delta = \text{prev\_percentage} - \text{curr\_percentage}$ and threshold check ($\ge 4.0\%$).
- [x] **Task 2.4**: Implement `evaluate_student_velocity()` method to produce structured `PendingGradeDropAlert` objects for courses exceeding threshold.

### Task Group 3: Early-Term Noise Suppression (User Story 2)
- [x] **Task 3.1**: Implement `is_noise_suppressed()` method checking if total graded points $< 100$ AND term active duration $< 21$ calendar days.
- [x] **Task 3.2**: Integrate noise suppression filter into `evaluate_student_velocity()` evaluation pipeline.

### Task Group 4: Silent Warming Protocol (User Story 3)
- [x] **Task 4.1**: Implement `is_silent_warming()` method checking if total student tracking duration is $< 7$ calendar days.
- [x] **Task 4.2**: Integrate silent warming check at start of `evaluate_student_velocity()` to suppress all alerts for un-warmed student baselines.

### Task Group 5: Test Suite & Validation (User Stories 1-3)
- [x] **Task 5.1**: Create comprehensive pytest suite `tests/test_velocity.py` covering rolling velocity drops, noise suppression edge cases, silent warming, and missing historical snapshot deferrals.
- [x] **Task 5.2**: Integrate `GradeVelocityEngine` into `src/main.py` batch runner workflow and verify test suite passes 100%.
