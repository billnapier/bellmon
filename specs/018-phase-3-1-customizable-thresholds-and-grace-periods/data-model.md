# Data Model: Phase 3.1 Customizable Notification Thresholds and Grace Periods

## 1. StudentPreferences Model

```python
class StudentPreferences(BaseModel):
    grace_period_hours: int = Field(default=36, ge=1, le=168, description="Digital missing work grace period in hours")
    velocity_drop_threshold: float = Field(default=4.0, ge=0.5, le=25.0, description="Grade drop velocity percentage trigger threshold")
    late_submission_threshold: int = Field(default=3, ge=1, le=20, description="Late submission count warning threshold within 7 days")
    workload_clumping_threshold: int = Field(default=2, ge=2, le=10, description="Minimum major assessments for workload clumping alert")
    workload_clumping_window_hours: int = Field(default=48, ge=12, le=168, description="Rolling time window in hours for workload clumping evaluation")
    weekend_grace_pause: bool = Field(default=True, description="Pause grace period clock during weekend hours")
```

## 2. Updated StudentSnapshot Entity

```python
class StudentSnapshot(BaseModel):
    student_id: str
    last_synced_at: datetime
    courses: Dict[str, CourseRecord] = Field(default_factory=dict)
    tracked_assignments: Dict[str, TrackedAssignment] = Field(default_factory=dict)
    attendance_events: List[AttendanceEventRecord] = Field(default_factory=list)
    late_submissions: List[CanvasSubmissionRecord] = Field(default_factory=list)
    preferences: StudentPreferences = Field(default_factory=StudentPreferences)
```

## 3. Firestore Document Representation

Under collection `students/{student_id}`:
```json
{
  "student_id": "student_123",
  "last_synced_at": "2026-09-01T12:00:00Z",
  "preferences": {
    "grace_period_hours": 24,
    "velocity_drop_threshold": 2.5,
    "late_submission_threshold": 2,
    "workload_clumping_threshold": 3,
    "workload_clumping_window_hours": 72,
    "weekend_grace_pause": true
  }
}
```
