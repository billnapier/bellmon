# Implementation Tasks: 011 Phase 2.1 Workload Clumping Radar

## Task List

- [ ] **Task 1: Define Radar Data Models** (`src/radar/models.py`)
  - Create Pydantic models: `AssessmentSummary`, `WorkloadCluster`, and `WorkloadRadarResult`.
- [ ] **Task 2: Implement Assessment Classification Logic** (`src/radar/engine.py`)
  - Implement keyword matching against title/category and point threshold checks ($\ge 50.0$).
- [ ] **Task 3: Implement 48-Hour Rolling Window Clustering Algorithm** (`src/radar/engine.py`)
  - Filter upcoming 7-day unsubmitted major assessments and group into 48h clusters.
- [ ] **Task 4: Export Radar Module Interface** (`src/radar/__init__.py`)
  - Expose `WorkloadRadarEngine`, `WorkloadCluster`, and `WorkloadRadarResult`.
- [ ] **Task 5: Write Comprehensive Unit Tests** (`tests/test_workload_radar.py`)
  - Test keyword classification, point threshold, time horizon, submission filter, and 48-hour cluster aggregation.
