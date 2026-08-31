# Data Model: Phase 1.6 Canvas Late Submission Tracking

## Schema Definitions

### `LateSubmissionRecord` (Pydantic Model)

```python
class LateSubmissionRecord(BaseModel):
    assignment_id: str
    course_id: str
    course_name: str = ""
    title: str
    due_at: Optional[str] = None         # ISO format string
    submitted_at: Optional[str] = None   # ISO format string
    minutes_late: int = 0
    detected_at: str                    # ISO format string
    is_late: bool = True
```

### Firestore Path Mapping
- Collection path: `students/{student_id}/late_submissions`
- Document ID: `{assignment_id}`

### Query Interface
- Retrieval method: `get_late_submissions(student_id: str, start_date: Optional[str] = None, end_date: Optional[str] = None) -> List[LateSubmissionRecord]`
