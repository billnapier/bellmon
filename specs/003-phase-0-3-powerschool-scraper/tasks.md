# Tasks: Phase 0.3 PowerSchool Playwright SAML SSO Scraper & Cookie Persistence

**Feature Branch**: `003-phase-0-3-powerschool-scraper` | **Spec**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

## Implementation Tasks

### Phase 1: Setup
- [x] T001 Define PowerSchool Pydantic data models (`PowerSchoolCourse`, `AttendanceRecord`, `SessionCookieStore`) in `src/ingestion/powerschool.py`

### Phase 2: Foundational Infrastructure
- [x] T002 Implement Secret Manager credential resolver for secret `powerschool-credentials` with environment variable fallback in `src/ingestion/powerschool.py`
- [x] T003 [P] Implement Firestore cookie store manager for reading and writing `psaid` session cookies under `students/{student_id}` in `src/ingestion/powerschool.py`

### Phase 3: User Story 1 - Session Cookie Reuse & Direct Navigation (P1)
- [x] T004 [P] [US1] Implement Playwright context cookie injection and direct navigation to guardian homepage in `src/ingestion/powerschool.py`
- [x] T005 [US1] Implement cookie validation logic to confirm active session state upon navigation in `src/ingestion/powerschool.py`

### Phase 4: User Story 2 - Automated SAML SSO Authentication Fallback (P1)
- [x] T006 [P] [US2] Implement Playwright automated SAML SSO form submission handling expired/missing cookies in `src/ingestion/powerschool.py`
- [x] T007 [US2] Implement session cookie extraction post-authentication and save to Firestore in `src/ingestion/powerschool.py`

### Phase 5: User Story 3 - PowerSchool Data Extraction (P1)
- [x] T008 [P] [US3] Implement HTML DOM parsing for course names, codes, letter grades, and percentages in `src/ingestion/powerschool.py`
- [x] T009 [US3] Implement HTML DOM parsing for period attendance codes (`A`, `CUT`, `T`, `U`) and dates in `src/ingestion/powerschool.py`

### Phase 6: Polish & Testing
- [x] T010 Implement test suite covering models, Firestore cookie caching, SAML SSO fallback, and DOM parsing in `tests/test_powerschool.py`
