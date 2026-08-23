# Tasks: Phase 0.4 Containerized Cloud Run Batch Runner & End-to-End PoC

**Feature**: Phase 0.4 Batch Runner PoC  
**Branch**: `004-phase-0-4-batch-runner-poc`  

## Implementation Tasks

### Phase 1: Setup

- [x] T001 Verify project structure and ensure `src/` and `terraform/` directories are prepared for batch runner modules.

### Phase 2: Foundational Work

- [x] T002 Define `BatchExecutionResult` and `StudentSnapshot` Pydantic models in `src/main.py`.

### Phase 3: User Story 1 - Unified Batch Orchestration CLI (Priority: P1)

**Story Goal**: Implement single entrypoint script (`src/main.py`) invoking Canvas & PowerSchool ingestion modules with stdout JSON logging.

- [x] T003 [US1] Implement `src/main.py` entrypoint orchestrating Canvas LMS and PowerSchool SIS ingestion.
- [x] T004 [P] [US1] Implement test suite in `tests/test_main.py` covering orchestrator execution, partial failure handling, and stdout JSON logs.

### Phase 4: User Story 2 - Containerized Playwright Cloud Run Execution (Priority: P1)

**Story Goal**: Package container image with Playwright Chromium and define GCP Cloud Run Job in Terraform.

- [x] T005 [US2] Create production `Dockerfile` installing Python 3.11 and Playwright Chromium dependencies.
- [x] T006 [P] [US2] Implement `terraform/cloud_run.tf` defining Cloud Run Job with 2GB memory allocation and 1 vCPU.

### Phase 5: User Story 3 - Scheduled Sub-Daily Execution Trigger (Priority: P2)

**Story Goal**: Automate execution via GCP Cloud Scheduler cron trigger.

- [x] T007 [US3] Implement `terraform/scheduler.tf` defining Cloud Scheduler HTTP authenticated trigger for Cloud Run Job.

### Phase 6: Polish & Verification

- [x] T008 Run `pytest` test suite and `terraform validate` to verify full feature implementation.
