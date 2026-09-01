# Research & Technical Analysis: Phase 3.1 Customizable Notification Thresholds and Grace Periods

## 1. Context & Design Decisions

### Decision 1: Per-Student Preference Storage in Firestore vs Global Config
* **Options Considered**:
  1. Environment variables / Config files (Global).
  2. Firestore per-student document field (`students/{student_id}.preferences`).
* **Selected Option**: Firestore per-student document field.
* **Rationale**: Multi-student households and families with students of different age levels require customized monitoring rules per student. Persisting preferences in Firestore per `student_id` enables granular family customization without service redeployments.

### Decision 2: Parameter Bounds & Validation
* **Grace Period**: 1 to 168 hours (7 days). Prevents zero or negative grace period values while allowing up to a full week buffer.
* **Grade Velocity Drop**: 0.5% to 25.0%. Prevents ultra-sensitive noise triggers (<0.5%) and unreasonable values (>25%).
* **Late Submission Threshold**: 1 to 20 occurrences.
* **Workload Clumping**: 2 to 10 assessments over 12 to 168 hours.

### Decision 3: Backward Compatibility Strategy
* Unconfigured or existing legacy Firestore student documents will not contain the `preferences` field.
* Using Pydantic `Field(default_factory=StudentPreferences)`, missing fields in Firestore dictionary automatically populate with standard default values upon deserialization, ensuring zero breaking changes for existing stored state.
