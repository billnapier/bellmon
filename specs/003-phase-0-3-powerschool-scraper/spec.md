# Feature Specification: Phase 0.3 PowerSchool Playwright SAML SSO Scraper & Cookie Persistence

**Feature Branch**: `003-phase-0-3-powerschool-scraper`  
**Created**: 2026-08-21  
**Status**: Draft  
**Input**: Phase 0.3 PowerSchool Playwright SAML SSO scraper with Firestore cookie persistence

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Session Cookie Reuse & Direct Navigation (Priority: P1)

As a monitoring engine, I want to retrieve previously saved session cookies (`psaid`) from Google Cloud Firestore and inject them into a Playwright browser context so that I can bypass full SAML SSO authentication on sub-daily runs and reduce scraping latency.

**Why this priority**: Bypassing SAML SSO on valid sessions dramatically reduces execution duration, CPU overhead, and authentication failure rate.

**Independent Test**: Running the Playwright scraper with valid stored cookies navigates directly to `/guardian/home.html` without redirecting to the SAML SSO login form.

**Acceptance Scenarios**:

1. **Given** valid session cookies stored in Firestore document `students/{student_id}`, **When** the scraper initializes, **Then** it injects cookies into Playwright browser context and navigates directly to guardian homepage.
2. **Given** direct navigation succeeds, **When** DOM renders, **Then** student grade dashboard is accessible immediately.

---

### User Story 2 - Automated SAML SSO Authentication Fallback (Priority: P1)

As a resilience-focused engine, I want the scraper to detect expired or missing session cookies, automatically execute SAML SSO credential login using credentials from GCP Secret Manager, and save updated session cookies back to Firestore.

**Why this priority**: Guarantees continuous data ingestion even when PowerSchool invalidates session cookies.

**Independent Test**: Running the scraper with expired or missing cookies triggers automated form submission on SAML SSO login page and updates Firestore with fresh cookies.

**Acceptance Scenarios**:

1. **Given** missing or expired session cookies in Firestore, **When** navigation to PowerSchool fails or redirects to SSO login, **Then** Playwright submits credentials from Secret Manager `powerschool-credentials`.
2. **Given** successful SAML SSO authentication, **When** target home page loads, **Then** updated session cookies (`psaid`) are saved to Firestore `students/{student_id}` with timestamp `updated_at`.

---

### User Story 3 - PowerSchool Data Extraction (Priority: P1)

As an academic sentinel, I want to extract course letter grades, percentage scores, period-level attendance, and assignment details from PowerSchool web pages so that missing work and grade velocity can be evaluated.

**Why this priority**: PowerSchool is the official SIS system of record for grades and attendance.

**Independent Test**: The parser extracts student performance tables into strongly-typed Python data structures (`PowerSchoolCourse`, `AttendanceEvent`).

**Acceptance Scenarios**:

1. **Given** loaded PowerSchool guardian homepage, **When** HTML content is parsed, **Then** it yields course codes, course titles, current percentage, letter grade, and period attendance.

---

### Edge Cases

- How does the system handle SAML SSO Multi-Factor Authentication (MFA) prompts if triggered?
  - Parent observer portal accounts bypass MFA for standard guardian login; if MFA is detected, engine logs a critical alert.
- What happens if PowerSchool is down for scheduled maintenance?
  - Retries up to 3 times before raising a non-fatal scraping failure alert.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST implement a Playwright headless Chromium scraper in `src/ingestion/powerschool.py`.
- **FR-002**: System MUST read/write session cookies (`psaid`) from/to GCP Firestore document `students/{student_id}`.
- **FR-003**: System MUST inspect cookie validity and execute SAML SSO authentication at `powerschool.bcp.org` if cookies are missing or expired.
- **FR-004**: System MUST retrieve SAML credentials from GCP Secret Manager `powerschool-credentials`.
- **FR-005**: System MUST extract course lists, letter grades, percentage scores, period attendance codes (`A`, `CUT`, `T`, `U`), and assignment scores into Python models (`PowerSchoolCourse`, `AttendanceRecord`).

### Key Entities

- **PowerSchoolCourse**: Represents an enrolled course in SIS (`course_code`, `name`, `letter_grade`, `percentage`).
- **AttendanceRecord**: Represents a period attendance event (`date`, `period`, `course`, `code`).
- **SessionCookieStore**: Session payload persisted in Firestore (`psaid`, `updated_at`).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Scraper completes data ingestion in under 10 seconds when using valid Firestore session cookies.
- **SC-002**: Automatic SAML SSO fallback succeeds 100% of the time when cookies expire without manual admin intervention.
- **SC-003**: Extraction accuracy for course percentage and attendance codes reaches 100% across test DOM snapshots.
