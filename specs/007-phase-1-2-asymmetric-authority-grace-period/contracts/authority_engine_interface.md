# Engine Contract: Asymmetric Authority & Grace Period Engine

## Interface Protocol

```python
from typing import List, Tuple
from datetime import datetime
from src.storage.models import TrackedAssignment
from src.engine.models import (
    CanvasAssignmentInput,
    PowerSchoolAssignmentInput,
    PendingMissingAlert,
    AssignmentStatus
)

class AsymmetricAuthorityEngine:
    def __init__(self, grace_period_hours: float = 36.0, timezone_str: str = "America/Los_Angeles"):
        ...

    def calculate_weekday_elapsed_hours(
        self, start_dt: datetime, end_dt: datetime
    ) -> float:
        """
        Calculate active hours between start_dt and end_dt, excluding
        the weekend blackout window (Friday 17:00:00 to Monday 08:00:00).
        """
        ...

    def evaluate_canvas_assignment(
        self,
        item: CanvasAssignmentInput,
        existing_tracked: TrackedAssignment | None,
        now: datetime
    ) -> Tuple[TrackedAssignment, PendingMissingAlert | None]:
        """
        Evaluates a single Canvas assignment against grace period or suppression rules.
        Returns updated TrackedAssignment and optional PendingMissingAlert.
        """
        ...

    def evaluate_powerschool_assignment(
        self,
        item: PowerSchoolAssignmentInput,
        existing_tracked: TrackedAssignment | None,
        now: datetime
    ) -> Tuple[TrackedAssignment, PendingMissingAlert | None]:
        """
        Evaluates a PowerSchool assignment record. If marked missing or score is 0,
        returns CONFIRMED_MISSING and queues a PendingMissingAlert.
        """
        ...
```
