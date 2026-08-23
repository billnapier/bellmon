# Research & Trade-off Decisions: Micro-Spec 0.3

**Feature Branch**: `003-phase-0-3-powerschool-scraper`

## 1. Browser Automation: Playwright for Python (Headless Chromium)
* **Decision**: Use `playwright.async_api` / `sync_api` for headless Chromium browser context management.
* **Rationale**: Playwright provides clean cookie context injection, fast async DOM parsing, robust wait-for-selector hooks, and headless execution suited for containerized GCP Cloud Run jobs.

## 2. Session Cookie Management: Firestore (`students/{student_id}`)
* **Decision**: Store session cookies (`psaid`) in Firestore document `students/{student_id}` under `session_cookie`.
* **Rationale**: Avoids re-authenticating through SAML SSO on every execution, reducing login latency from ~15s to <3s while staying within PowerSchool session TTL.

## 3. Credential Management: Secret Manager & Env Fallbacks
* **Decision**: Retrieve `powerschool-credentials` JSON payload from Secret Manager with fallback to `POWERSCHOOL_USERNAME` and `POWERSCHOOL_PASSWORD` env vars.
* **Rationale**: Maintains Zero-Trust security compliance while allowing seamless local testing and test fixture injection.

## 4. Custom Auth Model vs. Open-Source API Libraries
* **Decision**: Implement custom Playwright SAML SSO driver while using standard OSS parsing and data modeling libraries (`beautifulsoup4`, `pydantic`).
* **Rationale**: Existing PyPI PowerSchool libraries (e.g. `pypowerschool`, `powerschool-api`) require PowerSchool System Administrator OAuth plugin registration (`/oauth/access_token`). Because parent observers lack admin portal access on institutional domains (`powerschool.bcp.org`), custom browser-based SAML SSO authentication is strictly required. Standard OSS libraries are prioritized for data parsing and normalization.
