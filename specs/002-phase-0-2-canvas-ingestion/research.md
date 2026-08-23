# Research & Trade-off Decisions: Micro-Spec 0.2

**Feature Branch**: `002-phase-0-2-canvas-ingestion`

## 1. REST Client Framework: Python `requests` with Retry Session
* **Decision**: Standard `requests.Session` with `urllib3.util.retry.Retry` for automatic exponential backoff.
* **Rationale**: Simple, battle-tested, handles transient rate limiting (HTTP 429) and server errors (500, 502, 503, 504) cleanly without complex async dependencies.

## 2. Schema Validation: Pydantic v2
* **Decision**: Pydantic `BaseModel` data models for `CanvasAssignment` and `CanvasCourse`.
* **Rationale**: Automatic type validation, ISO timestamp parsing, alias mapping (`due_at`, `points_possible`), and clean serialization to JSON.
