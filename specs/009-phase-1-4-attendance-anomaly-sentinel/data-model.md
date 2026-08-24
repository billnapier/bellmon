# Data Model: Phase 1.4 Period Attendance Anomaly Sentinel

## 1. Enums

### `AttendanceCodeSeverity`
Location: `src/engine/models.py`

```python
from enum import Enum

class AttendanceCodeSeverity(str, Enum):
    P0_URGENT = "P0_URGENT"  # Immediate alert (A, CUT)
    P1_DIGEST = "P1_DIGEST"  # Sunday digest queue (T, U)
    IGNORED = "IGNORED"      # No action (P, E, EX, ACT)
```

## 2. Models

### `AttendanceRecordInput` (Pydantic V2)
Location: `src/engine/models.py`

```python
from pydantic import BaseModel
from typing import Optional

class AttendanceRecordInput(BaseModel):
    """Raw attendance record harvested from PowerSchool."""
    date: str             # Format: YYYY-MM-DD
    period: int           # Class period number (e.g. 1, 2, 3)
    course_name: str      # Name of the course (e.g. "Algebra II")
    code: str             # Attendance code (e.g. "A", "CUT", "T", "U", "P", "E")
    description: Optional[str] = None # Optional description (e.g. "Unexcused Absence")
```

### `AttendanceEvent` (Pydantic V2)
Location: `src/engine/models.py` & `src/storage/models.py`

```python
class AttendanceEvent(BaseModel):
    """Persisted attendance event record in Firestore ledger."""
    date: str
    period: int
    course_name: str
    code: str
    description: Optional[str] = None
    severity: AttendanceCodeSeverity
    notified: bool = False
    detected_at: str      # ISO timestamp
```

### `PendingAttendanceAlert` (Pydantic V2)
Location: `src/engine/models.py`

```python
class PendingAttendanceAlert(BaseModel):
    """Payload for P0 urgent attendance email alert."""
    student_id: str
    date: str
    period: int
    course_name: str
    code: str
    description: str
    severity: AttendanceCodeSeverity = AttendanceCodeSeverity.P0_URGENT
    detected_at: str      # ISO timestamp
```
