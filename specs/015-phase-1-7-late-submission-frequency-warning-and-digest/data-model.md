# Phase 1.7 Data Models & Schema Design

## 1. Dispatched Alert Record Model (`src/storage/models.py`)

Stores historical record of dispatched P0/P1 alerts for deduplication and cooldown checks.

```python
class DispatchedAlertRecord(BaseModel):
    """Ledger record for dispatched notifications/alerts."""
    alert_id: str
    alert_type: str  # e.g., "LATE_SUBMISSION_FREQUENCY_WARNING", "ATTENDANCE_P0"
    student_id: str
    dispatched_at: str  # ISO 8601 string
    metadata: Dict[str, Any] = Field(default_factory=dict)
```

Firestore Collection Path:
`students/{student_id}/dispatched_alerts/{alert_id}`

---

## 2. Late Submission Pattern Alert Model (`src/engine/models.py`)

Alert payload emitted by `LateSubmissionSentinel` when a student crosses the 7-day late frequency threshold.

```python
class LateSubmissionPatternAlert(BaseModel):
    """P1 Warning alert payload when late submission threshold is exceeded."""
    student_id: str
    count_in_window: int
    qualifying_records: List[LateSubmissionRecord] = Field(default_factory=list)
    detected_at: str  # ISO 8601 string
    severity: str = "P1_WARNING"
```

---

## 3. Sunday Digest Payload Extension (`src/notifications/digest.py`)

```python
class SundayDigestPayload(BaseModel):
    student_name: str
    digest_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    course_standings: List[Dict[str, Any]] = Field(default_factory=list)
    workload_radar: Optional[WorkloadRadarResult] = None
    upcoming_deadlines: List[Dict[str, Any]] = Field(default_factory=list)
    attendance_records: List[Dict[str, Any]] = Field(default_factory=list)
    tardy_count: int = 0
    unverified_count: int = 0
    # Spec 015 extensions:
    late_submissions: List[Dict[str, Any]] = Field(default_factory=list)
    late_count: int = 0
    has_late_warning: bool = False
```

---

## 4. Late Submission Digest Formatting Structure

Items in `late_submissions` list:
```python
{
    "course_name": "AP Physics C",
    "title": "Lab Report 3: Momentum",
    "minutes_late": 45,
    "formatted_delay": "45 min late",  # or "2.5 hrs late"
    "submitted_at": "2026-08-30T22:45:00Z"
}
```
