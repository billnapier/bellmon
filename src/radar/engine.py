"""Workload Clumping Radar Engine (Spec 011).

Detects clusters of major academic assessments (>= 2 major items due within 48 hours
over a forward 7-day time horizon).
"""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional
from src.radar.models import AssessmentSummary, WorkloadCluster, WorkloadRadarResult
from src.storage.models import StudentPreferences

DEFAULT_MAJOR_KEYWORDS = [
    "exam", "test", "project", "midterm", "final", "paper", "essay", "presentation", "lab"
]
DEFAULT_MIN_POINTS = 50.0
CLUMPING_WINDOW_HOURS = 48.0
HORIZON_DAYS = 7


class WorkloadRadarEngine:
    """Evaluates upcoming assignment schedules for workload clumping risk."""

    def __init__(
        self,
        keywords: Optional[List[str]] = None,
        min_points: float = DEFAULT_MIN_POINTS,
        clumping_window_hours: float = CLUMPING_WINDOW_HOURS,
        horizon_days: int = HORIZON_DAYS,
        clumping_threshold: int = 2,
        preferences: Optional[StudentPreferences] = None,
    ) -> None:
        if preferences is not None:
            self.clumping_window_hours = float(preferences.workload_clumping_window_hours)
            self.clumping_threshold = preferences.workload_clumping_threshold
        else:
            self.clumping_window_hours = clumping_window_hours
            self.clumping_threshold = clumping_threshold
        self.keywords = [k.lower() for k in (keywords or DEFAULT_MAJOR_KEYWORDS)]
        self.min_points = min_points
        self.horizon_days = horizon_days
        self.preferences = preferences

    def is_major_assessment(self, assignment: Dict[str, Any]) -> bool:
        """Determines if an assignment is a major assessment via category/title keyword or point value."""
        title = str(assignment.get("title", "")).lower()
        category = str(assignment.get("category", "")).lower()
        points = float(assignment.get("points_possible") or 0.0)

        # Point threshold check
        if points >= self.min_points:
            return True

        # Keyword match check
        for kw in self.keywords:
            if kw in title or kw in category:
                return True

        return False

    def _parse_datetime(self, val: Any) -> Optional[datetime]:
        if isinstance(val, datetime):
            if val.tzinfo is None:
                return val.replace(tzinfo=timezone.utc)
            return val
        if isinstance(val, str):
            try:
                dt = datetime.fromisoformat(val.replace("Z", "+00:00"))
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                return dt
            except ValueError:
                return None
        return None

    def evaluate(
        self,
        assignments: List[Dict[str, Any]],
        now: Optional[datetime] = None,
    ) -> WorkloadRadarResult:
        """Filters assignments within the forward 7-day horizon and groups major assessments into 48h clusters."""
        if now is None:
            now = datetime.now(timezone.utc)
        elif now.tzinfo is None:
            now = now.replace(tzinfo=timezone.utc)

        horizon_end = now + timedelta(days=self.horizon_days)

        major_items: List[AssessmentSummary] = []

        for item in assignments:
            # Skip if already submitted
            if item.get("has_submitted") or item.get("has_submitted_submissions"):
                continue

            due_dt = self._parse_datetime(item.get("due_at"))
            if not due_dt:
                continue

            # Must be strictly within [now, now + 7 days]
            if due_dt < now or due_dt > horizon_end:
                continue

            if self.is_major_assessment(item):
                summary = AssessmentSummary(
                    id=str(item.get("id", item.get("title"))),
                    title=str(item.get("title", "Untitled")),
                    course_name=str(item.get("course_name", "Unknown Course")),
                    due_at=due_dt,
                    points_possible=float(item.get("points_possible") or 0.0),
                    category=item.get("category"),
                    is_major=True,
                )
                major_items.append(summary)

        # Sort chronologically by due date
        major_items.sort(key=lambda x: x.due_at)

        # Form clusters using 48-hour rolling window
        clusters: List[WorkloadCluster] = []
        if not major_items:
            return WorkloadRadarResult(has_clumping=False, evaluated_at=now, clusters=[])

        current_cluster_items: List[AssessmentSummary] = []

        for item in major_items:
            if not current_cluster_items:
                current_cluster_items.append(item)
            else:
                # Check if item falls within 48h of the cluster's start time or previous item
                time_diff = (item.due_at - current_cluster_items[0].due_at).total_seconds() / 3600.0
                if time_diff <= self.clumping_window_hours:
                    current_cluster_items.append(item)
                else:
                    if len(current_cluster_items) >= self.clumping_threshold:
                        clusters.append(self._build_cluster(current_cluster_items))
                    current_cluster_items = [item]

        if len(current_cluster_items) >= self.clumping_threshold:
            clusters.append(self._build_cluster(current_cluster_items))

        return WorkloadRadarResult(
            has_clumping=len(clusters) > 0,
            evaluated_at=now,
            clusters=clusters,
        )

    def _build_cluster(self, items: List[AssessmentSummary]) -> WorkloadCluster:
        courses = sorted(list(set(item.course_name for item in items)))
        return WorkloadCluster(
            start_time=items[0].due_at,
            end_time=items[-1].due_at,
            courses=courses,
            assessments=items,
        )
