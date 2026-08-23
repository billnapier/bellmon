# Research & Trade-off Decisions: Micro-Spec 0.2

**Feature Branch**: `002-phase-0-2-canvas-ingestion`

## 1. REST Client Framework: Python `requests` with Retry Session
* **Decision**: Standard `requests.Session` with `urllib3.util.retry.Retry` for automatic exponential backoff.
* **Rationale**: Simple, battle-tested, handles transient rate limiting (HTTP 429) and server errors (500, 502, 503, 504) cleanly without complex async dependencies.

## 2. Schema Validation: Pydantic v2
* **Decision**: Pydantic `BaseModel` data models for `CanvasAssignment` and `CanvasCourse`.
* **Rationale**: Automatic type validation, ISO timestamp parsing, alias mapping (`due_at`, `points_possible`), and clean serialization to JSON.

## 3. Standard REST API & Open-Source Reuse (Principle 6 Compliance)
* **Decision**: Utilize standard open-source HTTP and validation packages (`requests`, `pydantic`, `urllib3`) to query Canvas LMS REST API.
* **Rationale**: Canvas LMS provides native REST API observer tokens (`Authorization: Bearer <token>`). Unlike PowerSchool's SAML SSO portal, Canvas supports official API tokens for parent observers, eliminating the need for browser automation (Playwright) and strictly adhering to Principle 6 (Open-Source First).
