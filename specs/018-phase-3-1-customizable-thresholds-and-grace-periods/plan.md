# Implementation Plan: Phase 3.1 Customizable Notification Thresholds and Grace Periods

**Feature ID**: `018-phase-3-1-customizable-thresholds-and-grace-periods`  
**Phase**: Phase 3 (Customization & Multi-Student Oversight)  

---

## 1. Technical Architecture & Component Changes

```
┌────────────────────────────────────────────────────────┐
│               StudentSnapshot Document                 │
│                 students/{student_id}                  │
│  - student_id: str                                     │
│  - courses: Dict                                       │
│  - tracked_assignments: Dict                           │
│  - preferences: StudentPreferences                     │
└───────────────────────────┬────────────────────────────┘
                            │ (Injected into engines)
                            ▼
┌────────────────────────────────────────────────────────┐
│                    Sentinel Engines                    │
├────────────────────────────────────────────────────────┤
│ 1. AuthorityEngine (grace_period_hours, weekend_pause)  │
│ 2. GradeVelocityEngine (velocity_drop_threshold)       │
│ 3. LateSubmissionSentinel (late_submission_threshold)  │
│ 4. WorkloadRadarEngine (clumping count & window_hours) │
└────────────────────────────────────────────────────────┘
```

## 2. File Modification Strategy

1. **`src/storage/models.py`**:
   - Define `StudentPreferences` Pydantic model with default values matching system constants.
   - Add `preferences: StudentPreferences = Field(default_factory=StudentPreferences)` field to `StudentSnapshot`.
2. **`src/storage/firestore.py`**:
   - Add `update_student_preferences(student_id: str, preferences: StudentPreferences) -> None` method.
   - Update `get_student_snapshot` to parse `preferences` field if present, defaulting to `StudentPreferences()` if missing.
3. **`src/engine/authority.py`**:
   - Update `evaluate_missing_assignments` to accept optional `preferences: Optional[StudentPreferences] = None`.
   - Use `preferences.grace_period_hours` and `preferences.weekend_grace_pause` when computing grace period expiration.
4. **`src/engine/velocity.py`**:
   - Update `evaluate_grade_velocity` to accept optional `preferences: Optional[StudentPreferences] = None`.
   - Compare grade drops against `preferences.velocity_drop_threshold` (default 4.0%).
5. **`src/engine/late_submissions.py`**:
   - Update `evaluate_late_submission_warning` to accept optional `preferences: Optional[StudentPreferences] = None`.
   - Use `preferences.late_submission_threshold` (default 3).
6. **`src/radar/engine.py`**:
   - Update `evaluate_workload_clumping` to accept optional `preferences: Optional[StudentPreferences] = None`.
   - Use `preferences.workload_clumping_threshold` (default 2) and `preferences.workload_clumping_window_hours` (default 48).
7. **`src/main.py`**:
   - In `run_batch()`, pass `student.preferences` to all engine calls.

## 3. Test Verification Strategy

- Add unit test file `tests/test_custom_preferences.py`:
  - Test default fallback behavior when no preferences are specified.
  - Test Authority engine with custom 24-hour grace period.
  - Test Velocity drop engine with custom 2.5% threshold.
  - Test Late Submission sentinel with custom 2-assignment threshold.
  - Test Workload Radar engine with custom 3-assessment / 72-hour window.
  - Test Firestore client preference persistence and retrieval.
