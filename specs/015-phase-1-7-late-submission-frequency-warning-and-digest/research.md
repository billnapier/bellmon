# Phase 1.7 Research & Technical Analysis

## Feature Overview
**Feature 015**: Phase 1.7 Late Submission Frequency Warning & Digest Integration.

This feature monitors Canvas assignment late submission trends across a rolling 7-day window. When a student submits 3 or more assignments late (where latency exceeds a configurable noise threshold `min_minutes_late`, default 5 minutes), the system generates a P1 warning alert and incorporates a detailed late submission summary into the Sunday Evening Digest.

---

## 1. Rolling 7-Day Window & Threshold Logic

### Requirement Analysis
- **Query Range**: Submissions evaluated must fall within the range `[now - 7 days, now]`.
- **Latency Threshold**: Submissions late by less than `min_minutes_late` (default 5 minutes) are ignored (e.g. 2 minutes late submission is excluded). Submissions with `minutes_late >= 5` are counted.
- **Frequency Trigger**: If count of qualifying late submissions $\ge 3$ within the 7-day window, trigger a P1 Late Submission Frequency Warning alert.

### Implementation Strategy
`LateSubmissionSentinel` in `src/engine/late_submissions.py`:
```python
def evaluate_late_submissions(
    self,
    student_id: str,
    records: List[LateSubmissionRecord],
    now: Optional[datetime] = None,
    min_minutes_late: int = 5,
    frequency_threshold: int = 3,
    dispatched_alerts: List[Dict[str, Any]] = None,
) -> Tuple[Optional[LateSubmissionPatternAlert], List[LateSubmissionRecord]]:
```
- Parse ISO timestamp `submitted_at` or `detected_at`.
- Check if timestamp is within `[now - 7 days, now]`.
- Filter `minutes_late >= min_minutes_late` and `is_late == True`.
- If qualifying records count $\ge 3$, evaluate alert ledger cooldown before generating `LateSubmissionPatternAlert`.

---

## 2. Alert Ledger & Cooldown Mechanism

### Requirement Analysis
- **7-Day Cooldown (168 hours)**: To prevent alert fatigue, once a P1 Late Submission Frequency Warning alert is sent for a student, no new standalone P1 warning email should be sent for 7 days (168 hours).
- **Persistence**: Store dispatched alert records in GCP Firestore under `students/{student_id}/dispatched_alerts/{alert_id}`.

### Firestore Ledger Schema
```json
{
  "alert_id": "late_freq_2026-08-31T12:00:00Z",
  "alert_type": "LATE_SUBMISSION_FREQUENCY_WARNING",
  "student_id": "student_123",
  "dispatched_at": "2026-08-31T12:00:00Z",
  "late_count": 3,
  "assignment_ids": ["canvas_101", "canvas_102", "canvas_103"]
}
```

---

## 3. Sunday Digest Integration

### Requirement Analysis
- The Sunday Evening Digest (Spec 012) runs weekly to summarize academic performance and workload.
- Must incorporate a **Late Submission Summary** section:
  1. Count of late submissions in the past 7 days.
  2. Detailed list of late submissions: Course, Assignment Title, Minutes/Hours Late, Submitted At.
  3. Chronic Late Submission Warning Banner if count $\ge 3$.

### Sunday Digest Payload Schema Update
Update `SundayDigestPayload` in `src/notifications/digest.py`:
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
    # Spec 015 additions:
    late_submissions: List[Dict[str, Any]] = Field(default_factory=list)
    late_count: int = 0
    has_late_warning: bool = False
```

---

## Technical Trade-offs & Decisions

| Decision Area | Selected Approach | Alternatives Considered | Rationale |
|---------------|-------------------|-------------------------|-----------|
| **Noise Filtering** | Ignore submissions late by $< 5$ mins (`min_minutes_late=5`). | Count all submissions late by $\ge 1$ min. | Network latency or clock drift shouldn't trigger parent alerts. |
| **Deduplication Cooldown** | 7-day cooldown (168h) per student. | 24-hour or 48-hour cooldown. | Prevents overwhelming parents with repetitive weekly warnings while still alerting on new weekly spikes. |
| **Digest Summary** | Always show late submission summary section in Sunday digest if late count $> 0$. | Only show in digest if count $\ge 3$. | Provides weekly visibility into minor late habits before they become chronic issues. |
