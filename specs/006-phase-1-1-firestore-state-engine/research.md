# Phase 0 Research: GCP Cloud Firestore State Persistence Engine

**Branch**: `006-phase-1-1-firestore-state-engine`  
**Date**: 2026-08-24  
**Spec**: [spec.md](./spec.md)

---

## 1. Storage SDK & Client Management

### Decision: `google-cloud-firestore` Python SDK
* **Chosen Solution**: Official `google-cloud-firestore` package (v2.x) with lazy client initialization.
* **Rationale**:
  * Native integration with GCP IAM authentication and Cloud Run runtime execution context.
  * Native support for document snapshots, sub-collections, field transformations (`ArrayUnion`, `SERVER_TIMESTAMP`), and transaction/batch semantics.
  * Aligns with Constitution Principle 6 (Open-Source First & Standard SDKs).
* **Alternatives Considered**:
  * *Raw REST API via `requests`*: Rejected due to missing connection pooling, lack of document transformation helpers, and manual auth token management overhead.
  * *Firebase Admin SDK*: Rejected because Cloud Firestore native client (`google-cloud-firestore`) is lighter-weight and avoids unnecessary Firebase app initialization overhead for server-side GCP workloads.

---

## 2. Local Testing & Mocking Strategy

### Decision: In-Memory Mock Client with Abstract Storage Protocol
* **Chosen Solution**: `FirestoreStateEngine` accepts a Firestore client instance or operates in `mock` mode via an in-memory dictionary-backed mock Firestore client (`MockFirestoreClient`).
* **Rationale**:
  * Enables 100% offline, isolated unit testing (`pytest`) without needing GCP network access or local Java-based Firestore emulator processes.
  * Guarantees fast test suite execution under CI environments (Principle 5 & Principle 1).
  * Mock client mirrors `google-cloud-firestore` document reference API (`collection().document().get()`, `set(merge=True)`, `update()`).
* **Alternatives Considered**:
  * *gcloud beta emulators firestore*: Requires Java runtime in CI environment, increasing GitHub Actions build setup time and container footprint.

---

## 3. Data Serialization & Model Validation

### Decision: Pydantic v2 Data Models (`src/storage/models.py`)
* **Chosen Solution**: Pydantic v2 `BaseModel` classes with `model_dump(mode='json')` and `model_validate()`.
* **Rationale**:
  * Type-safe validation before writing to Firestore, satisfying SC-002 (catching malformed state objects before persistence).
  * Native datetime serialization to ISO-8601 strings and automatic default factories for lists and dicts.
  * Native integration with Python typing.
* **Alternatives Considered**:
  * *Python dataclasses*: Lacks automatic runtime validation and coercion when parsing raw Firestore dictionary outputs.
  * *Raw Python dicts*: High risk of schema drift and key typo bugs across Phase 1 alert engines.

---

## 4. Atomic Updates & Document Structure

### Decision: Document-Level Merging (`merge=True`) & Atomic Array Appends
* **Chosen Solution**: Store student state at `students/{student_id}` as a root document with nested maps for `courses`, `tracked_assignments`, `attendance_events`, and `session_cookies`. Append grade history snapshots using `ArrayUnion` or explicit array append logic within model updates.
* **Rationale**:
  * `merge=True` ensures partial state updates (e.g. updating attendance without touching grade history) do not wipe other student state fields.
  * Prevents race conditions during batch updates across sub-daily executions.
* **Alternatives Considered**:
  * *Sub-collections for every assignment*: Overkills Firestore read quotas (1 read per assignment instead of 1 read per student document). Single student document per student optimizes read throughput and keeps latency under 200ms (SC-001).

---

## 5. Security & Session Cookie Storage

### Decision: Base64 / AES Encrypted Dict for `session_cookies`
* **Chosen Solution**: Session cookies are stored as encrypted JSON payloads within `students/{student_id}.session_cookies`.
* **Rationale**:
  * Complies with Principle 2 (Zero-Trust Secrets & Credential Isolation).
  * Prevents plaintext cookie leakage in Firestore web consoles.
* **Alternatives Considered**:
  * *Plaintext dict*: Risk of exposing active SAML session tokens to non-admin GCP IAM viewers.
