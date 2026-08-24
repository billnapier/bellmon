# Implementation Plan: Phase 1.5 SendGrid Responsive Email Router & Main Batch Integration

**Branch**: `010-phase-1-5-sendgrid-email-notification-router` | **Date**: 2026-08-24 | **Spec**: [spec.md](./spec.md)  
**Input**: Feature specification from `/specs/010-phase-1-5-sendgrid-email-notification-router/spec.md`

## Summary

Implement the responsive HTML email renderer and SendGrid Web API notification router in `src/notifications/`, then integrate the entire end-to-end pipeline into `src/main.py` (Ingestion -> Firestore State Load -> Alert Engine Evaluation -> Aggregated Email Dispatch -> Firestore Persist).

## Technical Context

**Language/Version**: Python 3.12  
**Primary Dependencies**: `pydantic` (v2), `urllib.request` / `requests`, `datetime`, `pytest`  
**Storage & Routing Integration**: `FirestoreStateEngine`, `NotificationRouter`, `SendGridClient`  
**Testing**: `pytest` (Isolated unit tests in `tests/test_notifications.py` and `tests/test_main.py`)  
**Target Platform**: Linux container (Cloud Run batch execution runtime)  
**Performance Goals**: Fast execution (< 500ms for template compilation & API request)  
**Constraints**: Send at most 1 combined email per student per daily run; zero duplicate alerts; graceful dry-run fallback when `SENDGRID_API_KEY` is absent.

## Constitution Check

- [x] **Principle 1 (Single Environment / Test-in-Prod)**: Isolated pytest unit tests and dry-run testing.
- [x] **Principle 2 (Zero-Trust Secrets)**: `SENDGRID_API_KEY` fetched dynamically from environment variables, fallback to dry-run mode if unconfigured.
- [x] **Principle 3 (Asymmetric System Authority)**: Notification dispatch triggered strictly after asymmetric authority engine evaluation.
- [x] **Principle 4 (Zero Fake Placeholders)**: Real HTML compilation, real REST endpoint specification, real status tracking.
- [x] **Principle 5 (PR-Only Enforcement & Mandatory CI Testing)**: Executed on feature branch `010-phase-1-5-sendgrid-email-notification-router`.
- [x] **Principle 6 (Open-Source First)**: Standard library and Pydantic.
- [x] **Principle 7 (Automated Container CI/CD)**: Handled via GitHub Actions pipeline on PR merge.

## Project Structure

### Documentation (this feature)

```text
specs/010-phase-1-5-sendgrid-email-notification-router/
├── spec.md              # Feature specification
├── plan.md              # Implementation plan (this file)
├── research.md          # Research & REST architecture design
├── data-model.md        # Data models (EmailPayload, DispatchResult)
├── quickstart.md        # Quickstart & test execution guide
└── contracts/
    └── notification_router_interface.md # Router & Client interface contract
```

### Source Code Layout

```text
src/
├── notifications/
│   ├── __init__.py
│   ├── models.py        # EmailPayload & DispatchResult models
│   ├── renderer.py      # Responsive HTML email template compiler
│   ├── sendgrid.py      # SendGrid REST API client
│   └── router.py        # NotificationRouter orchestrator
├── main.py              # Updated main batch runner with end-to-end orchestration
└── storage/
    └── engine.py        # Updated persistence hooks if required

tests/
├── test_notifications.py# Unit tests for renderer, SendGrid client, and router
└── test_main.py         # End-to-end orchestration unit tests
```

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|---|---|---|
| None | N/A | N/A |
