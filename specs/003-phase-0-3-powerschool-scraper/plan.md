# Implementation Plan: Phase 0.3 PowerSchool Playwright SAML SSO Scraper & Cookie Persistence

**Branch**: `003-phase-0-3-powerschool-scraper` | **Date**: 2026-08-22 | **Spec**: [spec.md](./spec.md)  
**Input**: Feature specification from `specs/003-phase-0-3-powerschool-scraper/spec.md`

## Summary

Implement the Python Playwright SAML SSO scraper for PowerSchool SIS in `src/ingestion/powerschool.py`. The module interacts with Google Cloud Firestore (`students/{student_id}`) to store/retrieve session cookies (`psaid`), retrieves SAML credentials securely from GCP Secret Manager secret `powerschool-credentials` (with env var fallback), executes automated SAML SSO login via Playwright headless Chromium when cookies are missing or expired, and extracts student grade and attendance data into strongly-typed Pydantic data models (`PowerSchoolCourse`, `AttendanceRecord`, `SessionCookieStore`).

## Technical Context

**Language/Version**: Python 3.11+  
**Primary Dependencies**: `playwright`, `pydantic`, `google-cloud-firestore`, `google-cloud-secretmanager`, `beautifulsoup4`, `pytest`  
**Storage**: GCP Firestore (`students/{student_id}`) for session cookie persistence  
**Testing**: `pytest` with mocked Playwright browser contexts, DOM fixtures, and Firestore/Secret Manager mocks  
**Target Platform**: GCP Cloud Run Jobs / Python runtime with Playwright Chromium drivers  
**Project Type**: Single project module (`src/ingestion/powerschool.py`)  
**Performance Goals**: Data ingestion completes in under 10 seconds with valid session cookies  
**Constraints**: Zero hardcoded credentials, automatic SAML SSO fallback, robust HTML DOM parsing  

## Constitution Check

- [x] **Zero-Trust Secrets**: SAML SSO credentials fetched from GCP Secret Manager `powerschool-credentials`.
- [x] **Asymmetric Authority**: Ingests PowerSchool SIS data independently without matching Canvas course names.
- [x] **Firestore Persistence**: Cookie session state stored cleanly under `students/{student_id}`.

## Project Structure

```text
src/
├── ingestion/
│   ├── __init__.py
│   └── powerschool.py    # PowerSchool Playwright scraper & cookie manager
tests/
└── test_powerschool.py   # Unit and integration test suite for PowerSchool scraper
```
