# Data Model: Phase 1.3 Grade Velocity Drop Sentinel

## 1. Alert Data Model

### `PendingGradeDropAlert` (Pydantic V2)
Location: `src/engine/models.py`

```python
class PendingGradeDropAlert(BaseModel):
    """Structured alert record for a detected grade velocity drop (>= 4.0%)."""
    course_id: str
    course_name: str
    prev_percentage: float
    curr_percentage: float
    delta: float
    detected_at: str  # ISO timestamp
```

## 2. Course Velocity Input Model

### `CourseVelocityInput` (Pydantic V2)
Location: `src/engine/models.py`

```python
class CourseVelocityInput(BaseModel):
    """Input parameters for course velocity drop evaluation."""
    course_id: str
    course_name: str
    current_percentage: float
    history: List[GradeSnapshot] = Field(default_factory=list)
    total_graded_points: Optional[float] = None
    term_active_days: Optional[int] = None
```

## 3. Student Velocity Context Model

### `StudentVelocityContext` (Pydantic V2)
Location: `src/engine/models.py`

```python
class StudentVelocityContext(BaseModel):
    """Context holding student registration and history tracking information for silent warming protocol."""
    student_id: str
    tracking_start_date: str  # Format: YYYY-MM-DD or ISO timestamp
    courses: List[CourseVelocityInput] = Field(default_factory=list)
```
