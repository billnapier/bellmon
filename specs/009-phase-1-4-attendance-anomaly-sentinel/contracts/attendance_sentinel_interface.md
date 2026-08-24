# Interface Contract: Attendance Sentinel Engine

## Module: `src/engine/attendance.py`

### Class: `AttendanceSentinel`

```python
class AttendanceSentinel:
    """Evaluates period-level attendance records against classification rules and deduplication state."""

    @staticmethod
    def classify_code(code: str) -> AttendanceCodeSeverity:
        """Categorize an attendance code into P0_URGENT, P1_DIGEST, or IGNORED.
        
        Rules:
        - 'A', 'CUT' -> P0_URGENT
        - 'T', 'U'   -> P1_DIGEST
        - 'P', 'E', 'EX', 'ACT', or unknown -> IGNORED
        """
        ...

    def evaluate_student_attendance(
        self,
        student_id: str,
        records: List[AttendanceRecordInput],
        existing_events: List[AttendanceEvent],
        now: Optional[datetime] = None
    ) -> Tuple[List[PendingAttendanceAlert], List[AttendanceEvent]]:
        """Evaluates raw attendance records for a student against existing ledger.
        
        Returns:
            Tuple of:
            - List[PendingAttendanceAlert]: New P0 urgent alerts to dispatch.
            - List[AttendanceEvent]: Complete updated list of attendance events for state persistence.
        """
        ...
```
