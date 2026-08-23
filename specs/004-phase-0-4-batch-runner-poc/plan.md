# Implementation Plan: Phase 0.4 Containerized Cloud Run Batch Runner & End-to-End PoC Verification

**Branch**: `004-phase-0-4-batch-runner-poc` | **Date**: 2026-08-23 | **Spec**: [spec.md](./spec.md)  
**Input**: Feature specification from `specs/004-phase-0-4-batch-runner-poc/spec.md`

## Summary

Implement the unified CLI batch orchestrator entrypoint in `src/main.py` that executes both Canvas LMS REST API ingestion (`src/ingestion/canvas.py`) and PowerSchool SIS Playwright SAML SSO scraping (`src/ingestion/powerschool.py`), logging formatted `StudentSnapshot` and `BatchExecutionResult` JSON payloads to stdout for GCP Cloud Logging. Create a production `Dockerfile` to package Python 3.11 with Playwright Chromium dependencies, and implement Terraform resources for Cloud Run Job (`terraform/cloud_run.tf`) and Cloud Scheduler (`terraform/scheduler.tf`).

## Technical Context

**Language/Version**: Python 3.11+  
**Primary Dependencies**: `playwright`, `pydantic`, `google-cloud-firestore`, `google-cloud-secretmanager`, `requests`, `pytest`  
**Infrastructure**: Terraform (Google Cloud Run Job, Google Cloud Scheduler, IAM roles)  
**Containerization**: Docker (`python:3.11-slim` + Playwright Chromium)  
**Testing**: `pytest` for unit testing `src/main.py` orchestrator; `terraform validate` for IaC syntax  
**Target Platform**: GCP Cloud Run Jobs (2GB RAM, 1 vCPU)  

## Constitution Check

- [x] **Test-in-Prod Single Environment**: Zero staging infrastructure overhead; single Cloud Run Job in production.
- [x] **Zero-Trust Secrets**: Secret Manager reference bindings in Terraform & dynamic lookup at runtime.
- [x] **Asymmetric Authority**: Ingests both Canvas and PowerSchool independently; logs dual snapshots.
- [x] **Zero Hardcoded Placeholders**: Dynamic GCP project resolution in environment variables and Terraform.
- [x] **PR-Only Enforcement**: Changes committed via git feature branch `004-phase-0-4-batch-runner-poc`.
- [x] **Open-Source First**: Standard Python logging, Pydantic data schemas, official Playwright & Terraform GCP provider.

## Project Structure

```text
src/
├── main.py                # Unified batch runner CLI entrypoint
├── ingestion/
│   ├── canvas.py          # Canvas API ingestion module
│   └── powerschool.py     # PowerSchool Playwright scraper module
Dockerfile                 # Playwright Python runtime container definition
terraform/
├── cloud_run.tf           # Cloud Run Job resource specification
└── scheduler.tf           # Cloud Scheduler cron trigger specification
tests/
└── test_main.py           # Test suite for batch runner orchestration CLI
```
