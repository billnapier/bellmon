# API & Interface Contract: FirestoreStateEngine Interface

**Branch**: `006-phase-1-1-firestore-state-engine`  
**Date**: 2026-08-24  
**Spec**: [spec.md](../spec.md)

---

## Abstract Python Interface Protocol (`src/storage/firestore.py`)

```python
from typing import Optional, List
from src.storage.models import StudentState, GradeSnapshot, SessionCookies

class StorageEngineInterface:
    """Abstract storage interface for reading and writing Bellmon student state."""

    def get_student_state(self, student_id: str) -> StudentState:
        """
        Retrieve student state document from Firestore.
        If document does not exist, return a default StudentState instance initialized with student_id.
        
        :param student_id: Unique student ID string.
        :return: Parsed StudentState object.
        """
        ...

    def update_student_state(self, student_id: str, state: StudentState) -> None:
        """
        Atomically persist student state object to Firestore at students/{student_id} using merge=True.
        
        :param student_id: Unique student ID string.
        :param state: StudentState object to persist.
        """
        ...

    def append_grade_snapshot(self, student_id: str, course_id: str, snapshot: GradeSnapshot) -> None:
        """
        Append a new dated GradeSnapshot object to courses.{course_id}.history array in Firestore.
        
        :param student_id: Unique student ID string.
        :param course_id: Unique course ID string.
        :param snapshot: GradeSnapshot instance containing date, percentage, letter_grade.
        """
        ...

    def get_grade_history(
        self, 
        student_id: str, 
        course_id: str, 
        start_days_ago: int = 10, 
        end_days_ago: int = 7
    ) -> List[GradeSnapshot]:
        """
        Query course grade snapshots for a student within a specific historical date window [t - start_days_ago, t - end_days_ago].
        
        :param student_id: Unique student ID string.
        :param course_id: Unique course ID string.
        :param start_days_ago: Beginning of historical window in days (default 10).
        :param end_days_ago: End of historical window in days (default 7).
        :return: List of GradeSnapshot objects matching the historical date window.
        """
        ...

    def save_session_cookies(self, student_id: str, cookies: SessionCookies) -> None:
        """
        Save encrypted PowerSchool SAML session cookies under student document.
        
        :param student_id: Unique student ID string.
        :param cookies: SessionCookies instance containing encrypted cookie payload.
        """
        ...

    def get_session_cookies(self, student_id: str) -> Optional[SessionCookies]:
        """
        Retrieve stored session cookies for a student, returning None if expired or missing.
        
        :param student_id: Unique student ID string.
        :return: SessionCookies instance or None.
        """
        ...
```

---

## Return Codes & Exceptions

| Exception Class | Cause | Resolution / Handling |
|---|---|---|
| `StorageValidationError` | Pydantic validation failed when building or validating `StudentState`. | Abort write; log error; do not write corrupted data to Firestore. |
| `FirestoreOperationError` | Network failure or GCP Firestore permission error. | Log exception details; retry with exponential backoff if transient. |
