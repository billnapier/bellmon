# Interface Contract: Grade Velocity Engine

## Class Definition: `GradeVelocityEngine`

Location: `src/engine/velocity.py`

### Interface Methods

```python
class GradeVelocityEngine:
    """Evaluates student academic course grade velocity drops and suppresses noisy or un-warmed alerts."""

    def evaluate_student_velocity(
        self,
        student_context: StudentVelocityContext,
        eval_date: Optional[date] = None,
    ) -> List[PendingGradeDropAlert]:
        """
        Evaluates grade velocity for all courses in a student's context.

        Args:
            student_context: Student velocity context including tracking start date and courses with history.
            eval_date: Optional evaluation date (defaults to current date in UTC).

        Returns:
            List[PendingGradeDropAlert]: List of triggered alerts for courses with delta >= 4.0%.
        """
        ...

    def is_silent_warming(
        self,
        tracking_start_date: Union[str, date],
        eval_date: date,
    ) -> bool:
        """
        Determines whether the student profile is in the initial 7-day silent warming window.

        Returns True if (eval_date - tracking_start_date).days < 7.
        """
        ...

    def is_noise_suppressed(
        self,
        total_graded_points: Optional[float],
        term_active_days: Optional[int],
    ) -> bool:
        """
        Determines whether alert should be suppressed due to early-term noise.

        Suppressed if total_graded_points < 100 AND term_active_days < 21.
        (If both attributes are None, default to not suppressed assuming mature course unless specified).
        """
        ...

    def find_baseline_snapshot(
        self,
        history: List[GradeSnapshot],
        eval_date: date,
    ) -> Optional[GradeSnapshot]:
        """
        Finds historical baseline snapshot in target range [eval_date - 10, eval_date - 7].
        Fallback range: [eval_date - 14, eval_date - 7].
        Returns None if no snapshot exists in range.
        """
        ...
```
