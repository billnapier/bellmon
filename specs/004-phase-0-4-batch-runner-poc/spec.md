# Feature Specification: Phase 0.4 Containerized Cloud Run Batch Runner & End-to-End PoC Verification

**Feature Branch**: `004-phase-0-4-batch-runner-poc`  
**Created**: 2026-08-21  
**Status**: Draft  
**Input**: Phase 0.4 Containerized Cloud Run batch job and Cloud Scheduler orchestration for end to end PoC

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Unified Batch Orchestration CLI (Priority: P1)

As a monitoring system runtime, I want a single entrypoint script (`src/main.py`) that invokes both Canvas LMS and PowerSchool SIS ingestion modules and logs formatted student snapshot records to stdout so that data harvesting execution is unified.

**Why this priority**: Ties together dual-system ingestion into a single executable command for containerized execution.

**Independent Test**: Executing `python -m src.main` runs both ingestion engines sequentially and outputs complete JSON snapshot payloads to stdout.

**Acceptance Scenarios**:

1. **Given** configured Canvas and PowerSchool credentials, **When** `python -m src.main` is invoked, **Then** it triggers Canvas API ingestion followed by PowerSchool Playwright scraping.
2. **Given** successful ingestion, **When** script finishes, **Then** student course, missing assignment, and attendance snapshots are printed to stdout as JSON records and exit code is 0.

---

### User Story 2 - Containerized Playwright Cloud Run Execution (Priority: P1)

As an ops engineer, I want the Python runtime and Playwright headless Chromium dependencies packaged into a Docker container image and deployed as a GCP Cloud Run Job via Terraform so that execution is 100% serverless and zero-cost within GCP free tier limits.

**Why this priority**: Guarantees container portability and eliminates dedicated server overhead.

**Independent Test**: Building the `Dockerfile` and executing the container on GCP Cloud Run Job completes execution successfully.

**Acceptance Scenarios**:

1. **Given** a `Dockerfile` installing Python 3.11 and Playwright Chromium binaries, **When** built and pushed to GCP Artifact Registry, **Then** Cloud Run Job executes container without missing system library errors.
2. **Given** Terraform definition for Cloud Run Job, **When** deployed via Guardian, **Then** job is runnable on-demand or via Cloud Scheduler HTTP trigger.

---

### User Story 3 - Scheduled Sub-Daily Execution Trigger (Priority: P2)

As a system maintainer, I want Cloud Scheduler to trigger the Cloud Run Job sub-daily (e.g., 5:00 PM weekdays) so that student performance snapshots are harvested automatically without manual trigger.

**Why this priority**: Automates monitoring execution to establish data history snapshots before Phase 1 alert rules are implemented.

**Independent Test**: Triggering Cloud Scheduler manually executes Cloud Run Job and generates Cloud Logging entries.

**Acceptance Scenarios**:

1. **Given** Cloud Scheduler trigger defined in `terraform/scheduler.tf`, **When** schedule fires, **Then** Cloud Run Job execution is initiated via GCP IAM authenticated HTTP call.

---

### Edge Cases

- How does the batch runner handle failure in one system (e.g., Canvas works but PowerSchool times out)?
  - Partial ingestion results are logged; job records error metric to GCP Cloud Monitoring without crashing ungracefully.
- What container memory and CPU limits are required for Playwright Chromium?
  - Configures 2GB RAM and 1 vCPU allocation in Cloud Run Job definition to prevent OOM errors during browser rendering.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST implement a unified batch orchestrator entrypoint in `src/main.py`.
- **FR-002**: System MUST package runtime into a Dockerfile including Python 3.11 and Playwright Chromium browser binaries.
- **FR-003**: System MUST define Cloud Run Job resource definitions in `terraform/cloud_run.tf` with 2GB memory allocation.
- **FR-004**: System MUST define Cloud Scheduler cron triggers in `terraform/scheduler.tf` targeting Cloud Run Job.
- **FR-005**: System MUST log dual-system student snapshots to stdout/Cloud Logging in JSON format.

### Key Entities

- **BatchExecutionResult**: Execution telemetry record (`timestamp`, `status`, `canvas_status`, `powerschool_status`, `duration_seconds`).
- **StudentSnapshot**: Harvested data snapshot (`student_id`, `timestamp`, `courses`, `missing_assignments`, `attendance_events`).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: End-to-end Cloud Run Job execution completes in under 45 seconds from cold start to log output.
- **SC-002**: Cloud Run Job container execution succeeds 100% of the time without Playwright browser launch failures.
- **SC-003**: GCP Cloud Logging captures structured JSON logs for verified student snapshots on every execution.
