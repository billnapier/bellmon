# Technical Research: Phase 0.4 Containerized Cloud Run Batch Runner & End-to-End PoC

**Feature Branch**: `004-phase-0-4-batch-runner-poc`  
**Date**: 2026-08-23  

## Research & Technical Decisions

### Decision 1: Entrypoint & Log Format (`src/main.py`)
- **Decision**: `src/main.py` will serve as the main execution entrypoint. It will invoke `ingest_canvas_data()` and `ingest_powerschool_data()` sequentially.
- **Rationale**: Sequential invocation keeps container memory overhead low and prevents CPU contention while Playwright Chromium runs. Structured JSON records printed to stdout are automatically parsed into severity/jsonPayload by GCP Cloud Logging.
- **Alternatives Considered**: Parallel `asyncio` execution was evaluated, but sequential execution avoids memory spikes during Playwright browser rendering on 2GB RAM Cloud Run instances.

### Decision 2: Playwright Headless Docker Image Structure (`Dockerfile`)
- **Decision**: Standardize on `python:3.11-slim` base image, installing required system packages, `playwright`, and executing `playwright install --with-deps chromium` (or `playwright install chromium` with Debian lib dependencies).
- **Rationale**: Minimal image size (~600MB-1GB) with pre-installed Chromium dependencies ensures reliable execution in Cloud Run container jobs without missing dynamic library errors.
- **Alternatives Considered**: Heavy official Playwright docker images (e.g. `mcr.microsoft.com/playwright/python:v1.40.0-jammy`) were evaluated but are unnecessarily large (>2GB) for Cloud Run container deployment.

### Decision 3: Cloud Run Job Terraform Specification (`terraform/cloud_run.tf`)
- **Decision**: Define a `google_cloud_run_v2_job` resource with memory limit set to `2Gi` and CPU limit set to `1000m` (1 vCPU), specifying task timeout and execution service account.
- **Rationale**: Meets FR-003 and SC-001 by providing sufficient memory for Playwright headless Chromium while keeping execution costs within GCP free tier / minimal cost footprint.

### Decision 4: Cloud Scheduler Terraform Specification (`terraform/scheduler.tf`)
- **Decision**: Define a `google_cloud_scheduler_job` resource using a cron schedule (e.g. `0 17 * * 1-5` for 5 PM weekdays) targeting the Cloud Run Job REST API v1/v2 execution endpoint via `http_target` with OAuth/OIDC token service account credentials.
- **Rationale**: Automated sub-daily trigger (FR-004) without human intervention, using GCP native IAM authentication.
