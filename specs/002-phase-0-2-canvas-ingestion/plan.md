# Implementation Plan: Phase 0.2 Canvas LMS REST API Ingestion Module

**Branch**: `002-phase-0-2-canvas-ingestion` | **Date**: 2026-08-21 | **Spec**: [spec.md](./spec.md)  
**Input**: Feature specification from `specs/002-phase-0-2-canvas-ingestion/spec.md`

## Summary

Implement the Python Canvas LMS REST API ingestion client in `src/ingestion/canvas.py`. The module retrieves Canvas access tokens securely from GCP Secret Manager secret `canvas-api-token` (with local env fallback `CANVAS_API_TOKEN`), queries student observee course enrollments (`GET /api/v1/courses`) and missing digital submissions (`GET /api/v1/users/:observee_id/missing_submissions`), and normalizes API payloads into strongly-typed Pydantic data models (`CanvasAssignment`, `CanvasCourse`).

## Technical Context

**Language/Version**: Python 3.11+  
**Primary Dependencies**: `requests`, `pydantic`, `google-cloud-secretmanager`, `pytest`  
**Storage**: In-memory data structures, normalized for downstream Firestore ingestion  
**Testing**: `pytest` with mocked HTTP API fixtures and live integration capabilities  
**Target Platform**: GCP Cloud Run Jobs / Python runtime  
**Project Type**: Single project module (`src/ingestion/canvas.py`)  
**Performance Goals**: API response parsing completes in under 2 seconds for up to 50 assignments  
**Constraints**: Zero hardcoded plain-text tokens, exponential backoff for HTTP 429/5xx errors  

## Constitution Check

- [x] **Zero-Trust Secrets**: Access token fetched from GCP Secret Manager runtime or local env.
- [x] **Asymmetric Authority**: Ingests Canvas data independently without title matching.

## Project Structure

```text
src/
├── ingestion/
│   ├── __init__.py
│   └── canvas.py         # Canvas LMS REST API ingestion client
tests/
└── test_canvas.py        # Unit and integration test suite for Canvas ingestion
```
