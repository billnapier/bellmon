# Technical Plan: 011 Phase 2.1 Workload Clumping Radar

## Architecture & Module Structure

```
src/
├── radar/
│   ├── __init__.py
│   ├── models.py       # Pydantic schemas for WorkloadRadar payloads
│   └── engine.py       # WorkloadRadarEngine class and evaluation logic
tests/
└── test_workload_radar.py  # Unit tests for classification and clumping
```

## Technical Specification & Interfaces

### Class `WorkloadRadarEngine`
```python
class WorkloadRadarEngine:
    def __init__(self, keywords: list[str] = None, min_points: float = 50.0):
        ...
        
    def is_major_assessment(self, assignment: dict) -> bool:
        """Determines if assignment qualifies as major by category/title keyword or point value."""
        ...

    def evaluate(self, assignments: list[dict], now: datetime = None) -> WorkloadRadarResult:
        """Filters assignments within 7-day horizon and groups major assessments into 48h clusters."""
        ...
```

## Key Test Scenarios
1. **Keyword Classification**: Verify 'Unit Exam', 'Final Project', 'Midterm' trigger major classification regardless of points.
2. **Points Threshold**: Verify 50.0 point daily assignment triggers major classification.
3. **Horizon Filter**: Verify items > 7 days in future or in the past are excluded.
4. **Submitted Filter**: Verify submitted assignments are ignored.
5. **Clumping Window**: Verify 2 items within 48h generate a cluster; 2 items 50h apart do not.
6. **Multi-Course Aggregation**: Verify exams in Math and Physics within 24h are combined in a cluster with both courses listed.
