# Feature Specification: Phase 3.1 Customizable Notification Thresholds and Grace Periods

**Feature ID**: `018-phase-3-1-customizable-thresholds-and-grace-periods`  
**Phase**: Phase 3 (Customization & Multi-Student Oversight)  
**Status**: Draft  
**Created**: 2026-09-01  

---

## 1. Executive Summary & Goals

### 1.1 Overview
Currently, Bellmon evaluates academic risks using global default parameters: a 36-hour digital missing work grace period, a 4.0% grade drop velocity trigger, a 3-occurrence late submission frequency warning threshold, and a 2-assessment/48-hour workload clumping filter.

Phase 3.1 introduces **Customizable Notification Thresholds and Grace Periods**, allowing parents and guardians to tailor monitoring sensitivity per student/observee without code changes or service redeployments. Custom configurations are persisted in Google Cloud Firestore under `students/{student_id}` as a `preferences` object and dynamically injected into sentinel evaluation engines.

### 1.2 User Stories
* **US-1 (Custom Grace Period)**: As a parent, I want to adjust the digital missing work grace period (e.g., to 24 hours or 48 hours) for my student so that notifications match our family's expectations for homework accountability.
* **US-2 (Custom Grade Drop Sensitivity)**: As a parent, I want to configure the grade velocity drop threshold percentage (e.g., 2.0% or 5.0%) so that I am alerted to grade drops appropriate for my student's academic level.
* **US-3 (Custom Workload & Late Submission Sensitivity)**: As a parent, I want to adjust the late submission warning frequency threshold (e.g., 2 or 4 assignments) and workload clumping radar thresholds (e.g., 3 assessments in 72 hours).
* **US-4 (Backwards Compatibility & Safe Defaults)**: As a system operator, I want unconfigured or partially configured student records to automatically fall back to standard system defaults so existing operations remain 100% stable.

---

## 2. Functional Requirements

### 2.1 Configuration Schema & Storage
* Extend `StudentPreferences` Pydantic model and Firestore schema within `src/storage/models.py`:
  * `grace_period_hours: int = Field(default=36, ge=1, le=168)`
  * `velocity_drop_threshold: float = Field(default=4.0, ge=0.5, le=25.0)`
  * `late_submission_threshold: int = Field(default=3, ge=1, le=20)`
  * `workload_clumping_threshold: int = Field(default=2, ge=2, le=10)`
  * `workload_clumping_window_hours: int = Field(default=48, ge=12, le=168)`
  * `weekend_grace_pause: bool = Field(default=True)`
* Embed `preferences: StudentPreferences = Field(default_factory=StudentPreferences)` into `StudentSnapshot` and Firestore document `students/{student_id}`.

### 2.2 Dynamic Engine Overrides
* **Authority Engine (`src/engine/authority.py`)**: Update grace period evaluation logic to utilize `preferences.grace_period_hours` and `preferences.weekend_grace_pause` when provided, falling back to 36h default if unconfigured.
* **Grade Velocity Engine (`src/engine/velocity.py`)**: Update grade trajectory drop check to use `preferences.velocity_drop_threshold` (e.g. comparing $\Delta \ge \text{threshold}$), replacing hardcoded 4.0%.
* **Late Submission Sentinel (`src/engine/late_submissions.py`)**: Update frequency alert evaluator to use `preferences.late_submission_threshold`, replacing hardcoded 3 occurrences.
* **Workload Radar Engine (`src/radar/engine.py`)**: Update workload clumping detector to use `preferences.workload_clumping_threshold` and `preferences.workload_clumping_window_hours`.

### 2.3 Data Ingestion & Firestore Operations
* Support updating student preferences via Firestore client `update_student_preferences(student_id, preferences: StudentPreferences)`.
* Ensure `get_student_snapshot()` gracefully reads `preferences` from Firestore document, falling back to `StudentPreferences()` defaults if missing or incomplete.

---

## 3. Acceptance Criteria

1. **AC-1 (Schema Validation)**: `StudentPreferences` model validates parameters within bounds (grace period 1–168h, drop threshold 0.5–25.0%, etc.) and provides standard defaults (36h, 4.0%, 3, 2, 48h, True).
2. **AC-2 (Authority Grace Override)**: Authority engine correctly triggers alerts after custom `grace_period_hours` (e.g., 24h) instead of 36h when custom preferences are present.
3. **AC-3 (Velocity Threshold Override)**: Grade velocity engine triggers alerts when grade drop exceeds custom `velocity_drop_threshold` (e.g., 2.5%) and suppresses drops below custom threshold.
4. **AC-4 (Late Submission Threshold Override)**: Late submission sentinel triggers warning when late submission count reaches custom `late_submission_threshold` (e.g., 2).
5. **AC-5 (Workload Radar Override)**: Radar engine identifies assessment clusters based on custom `workload_clumping_threshold` and `workload_clumping_window_hours`.
6. **AC-6 (Firestore Integration & Fallback)**: Firestore client correctly serializes and deserializes `preferences` field without breaking legacy student records lacking the field.
7. **AC-7 (Test Suite Pass)**: All 84 existing unit tests continue to pass without regression, and new unit tests for custom preference overrides pass.
