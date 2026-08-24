"""Pydantic models for Workload Clumping Radar (Spec 011)."""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class AssessmentSummary(BaseModel):
    """Summary of a single major assignment or assessment."""
    id: str
    title: str
    course_name: str
    due_at: datetime
    points_possible: float = 0.0
    category: Optional[str] = None
    is_major: bool = True


class WorkloadCluster(BaseModel):
    """A cluster of 2 or more major assessments occurring within a 48-hour window."""
    start_time: datetime
    end_time: datetime
    courses: List[str] = Field(default_factory=list)
    assessments: List[AssessmentSummary] = Field(default_factory=list)

    @property
    def total_major_items(self) -> int:
        return len(self.assessments)


class WorkloadRadarResult(BaseModel):
    """Overall evaluation result of the Workload Clumping Radar."""
    has_clumping: bool = False
    evaluated_at: datetime
    clusters: List[WorkloadCluster] = Field(default_factory=list)
