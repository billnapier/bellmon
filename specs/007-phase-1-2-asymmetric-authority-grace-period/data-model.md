# Data Model & Schema Specification: Phase 1.2

## Enums

### `AssignmentStatus` (String Enum)

- `NEW`: Initial state before evaluation.
- `GRACE_PERIOD`: Canvas digital assignment in 36-hour grace period.
- `EXPIRED`: 36 weekday grace hours elapsed without submission.
- `CONFIRMED_MISSING`: PowerSchool assignment with `isMissing: true` or `score: 0`.
- `RESOLVED`: Assignment submitted or missing flag cleared.
- `SUPPRESSED`: Canvas missing assignment with submission type `on_paper` or `none`.

### `AlertSource` (String Enum)

- `CANVAS_GRACE_EXPIRED`: Alert triggered due to 36-hour grace period expiration.
- `POWERSCHOOL_CONFIRMED`: Alert triggered immediately by PowerSchool official missing status or zero score.

---

## Data Structures

### `PendingMissingAlert` (Pydantic Model)

```python
class PendingMissingAlert(BaseModel):
    assignment_id: str
    title: str
    course_id: str
    due_at: Optional[str] = None  # ISO timestamp string
    source: AlertSource  # CANVAS_GRACE_EXPIRED | POWERSCHOOL_CONFIRMED
    points_possible: Optional[float] = None
    detected_at: str  # ISO timestamp string
```

### `CanvasAssignmentInput` (Pydantic Model / Dict)

```python
class CanvasAssignmentInput(BaseModel):
    assignment_id: str
    title: str
    course_id: str
    due_at: str
    submission_types: List[str]  # e.g., ["online_upload"], ["on_paper"], ["none"]
    is_missing: bool
```

### `PowerSchoolAssignmentInput` (Pydantic Model / Dict)

```python
class PowerSchoolAssignmentInput(BaseModel):
    assignment_id: str
    title: str
    course_id: str
    due_at: Optional[str] = None
    is_missing: bool
    score: Optional[float] = None
    points_possible: Optional[float] = None
```

---

## State Transition Rules

| Initial Status | Condition | New Status | Alert Generated? |
|---|---|---|---|
| (None / NEW) | Canvas `is_missing: true` AND `submission_types` has `online_upload` | `GRACE_PERIOD` | No |
| (None / NEW) | Canvas `is_missing: true` AND `submission_types` in `['on_paper', 'none']` | `SUPPRESSED` | No |
| `GRACE_PERIOD` | Elapsed active weekday hours >= 36.0 | `EXPIRED` | Yes (`CANVAS_GRACE_EXPIRED`) |
| `GRACE_PERIOD` | Canvas `is_missing: false` (submitted/cleared) | `RESOLVED` | No |
| Any | PowerSchool `is_missing: true` OR `score: 0` | `CONFIRMED_MISSING` | Yes (`POWERSCHOOL_CONFIRMED`) |
