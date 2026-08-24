# Quickstart Guide: GCP Cloud Firestore State Engine

**Branch**: `006-phase-1-1-firestore-state-engine`  
**Date**: 2026-08-24  
**Spec**: [spec.md](./spec.md)

---

## 1. Environment Setup

Verify Python 3.11+ environment and dependencies:

```bash
# Ensure standard dependencies are installed
pip install pytest pydantic google-cloud-firestore
```

---

## 2. Running Offline Unit Tests (Mock Mode)

Run the storage engine unit tests using the isolated, in-memory mock client (no GCP credentials required):

```bash
# Run pytest specifically for the firestore storage layer
pytest tests/test_firestore.py -v
```

---

## 3. Dynamic Live Environment Querying & Firestore Test (Optional GCP Integration)

To test against live GCP Cloud Firestore in your active GCP project, run copy-paste commands that dynamically derive your environment configuration:

```bash
# Dynamically query active GCP project ID from gcloud CLI (Principle 4 compliance)
export GCP_PROJECT_ID=$(gcloud config get-value project 2>/dev/null || echo "")

if [ -z "$GCP_PROJECT_ID" ]; then
    echo "No active gcloud project set. Using mock mode for tests."
else
    echo "Active GCP Project: $GCP_PROJECT_ID"
    # Ensure Firestore DB is initialized in native mode
    gcloud firestore databases describe --project="$GCP_PROJECT_ID" 2>/dev/null || echo "Initialize Firestore Database in GCP Console if not present."
fi
```

---

## 4. Example Usage Snippet

```python
from src.storage.firestore import FirestoreStateEngine
from src.storage.models import StudentState, CourseState, GradeSnapshot

# Initialize engine in mock mode for testing/local dev
engine = FirestoreStateEngine(use_mock=True)

# Read or initialize student state
student = engine.get_student_state("student_12345")
print(f"Student ID: {student.student_id}, Courses: {len(student.courses)}")

# Append a grade snapshot
snapshot = GradeSnapshot(date="2026-08-24", percentage=92.5, letter_grade="A-")
engine.append_grade_snapshot("student_12345", "MATH-101", snapshot)

# Retrieve updated state
updated_student = engine.get_student_state("student_12345")
print("Grade History:", updated_student.courses["MATH-101"].history)
```
