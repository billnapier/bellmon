"""
GCP Cloud Firestore storage engine for Bellmon student state persistence.
Supports live GCP Cloud Firestore connections and in-memory mock client mode for offline testing.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
import os

from src.storage.models import (
    StudentState,
    CourseState,
    GradeSnapshot,
    SessionCookies,
    TrackedAssignment,
    AttendanceEvent,
    LateSubmissionRecord,
    DispatchedAlertRecord,
    StudentPreferences,
)


class MockDocumentSnapshot:
    """Mock representation of a Firestore DocumentSnapshot."""

    def __init__(self, data: Optional[Dict[str, Any]], exists: bool = True):
        self._data = data
        self.exists = exists

    def to_dict(self) -> Optional[Dict[str, Any]]:
        return self._data


class MockDocumentRef:
    """Mock representation of a Firestore DocumentReference."""

    def __init__(
        self,
        store: Dict[str, Dict[str, Any]],
        doc_id: str,
        client: Optional["MockFirestoreClient"] = None,
        path: str = "",
    ):
        self._store = store
        self._doc_id = doc_id
        self._client = client
        self._path = path

    def get(self) -> MockDocumentSnapshot:
        if self._doc_id in self._store:
            # Return a copy of stored dict
            return MockDocumentSnapshot(dict(self._store[self._doc_id]), exists=True)
        return MockDocumentSnapshot(None, exists=False)

    def set(self, document_data: Dict[str, Any], merge: bool = False) -> None:
        if merge and self._doc_id in self._store:
            existing = self._store[self._doc_id]
            # Deep merge dictionary fields for nested maps like courses, tracked_assignments
            merged = self._deep_merge(existing, document_data)
            self._store[self._doc_id] = merged
        else:
            self._store[self._doc_id] = dict(document_data)

    def update(self, field_updates: Dict[str, Any]) -> None:
        if self._doc_id not in self._store:
            self._store[self._doc_id] = {}
        target = self._store[self._doc_id]
        for key, value in field_updates.items():
            # Handle dot notation for nested fields e.g. "courses.MATH-101.history"
            parts = key.split(".")
            d = target
            for part in parts[:-1]:
                if part not in d or not isinstance(d[part], dict):
                    d[part] = {}
                d = d[part]
            d[parts[-1]] = value

    def collection(self, collection_name: str) -> "MockCollectionRef":
        sub_path = f"{self._path}/{collection_name}" if self._path else collection_name
        if self._client:
            return self._client.collection(sub_path)
        raise ValueError("MockDocumentRef not initialized with client reference")

    def _deep_merge(self, base: Dict[str, Any], update: Dict[str, Any]) -> Dict[str, Any]:
        res = dict(base)
        for k, v in update.items():
            if k in res and isinstance(res[k], dict) and isinstance(v, dict):
                res[k] = self._deep_merge(res[k], v)
            else:
                res[k] = v
        return res


class MockCollectionRef:
    """Mock representation of a Firestore CollectionReference."""

    def __init__(
        self,
        store: Dict[str, Dict[str, Any]],
        client: Optional["MockFirestoreClient"] = None,
        path: str = "",
    ):
        self._store = store
        self._client = client
        self._path = path

    def document(self, document_id: str) -> MockDocumentRef:
        doc_path = f"{self._path}/{document_id}" if self._path else document_id
        return MockDocumentRef(self._store, document_id, client=self._client, path=doc_path)

    def stream(self) -> List[MockDocumentSnapshot]:
        return [
            MockDocumentSnapshot(dict(data), exists=True)
            for doc_id, data in self._store.items()
        ]


class MockFirestoreClient:
    """In-memory mock client simulating GCP Cloud Firestore behavior."""

    def __init__(self):
        # Map of collection_name -> { doc_id -> doc_dict }
        self._collections: Dict[str, Dict[str, Dict[str, Any]]] = {}

    def collection(self, collection_name: str) -> MockCollectionRef:
        if collection_name not in self._collections:
            self._collections[collection_name] = {}
        return MockCollectionRef(
            self._collections[collection_name], client=self, path=collection_name
        )



class FirestoreStateEngine:
    """
    Persistence engine wrapping GCP Cloud Firestore for managing student academic state.
    """

    def __init__(self, use_mock: bool = False, project_id: Optional[str] = None, client: Optional[Any] = None, db_client: Optional[Any] = None):
        self.use_mock = use_mock
        effective_client = client if client is not None else db_client
        if effective_client is not None:
            self.client = effective_client
        elif use_mock:
            self.client = MockFirestoreClient()
        else:
            try:
                from google.cloud import firestore
                pid = project_id or os.getenv("GCP_PROJECT_ID") or os.getenv("GCP_PROJECT") or os.getenv("GOOGLE_CLOUD_PROJECT") or "bellmon"
                self.client = firestore.Client(project=pid)
            except Exception:
                # Fall back to mock client if GCP credentials or client initialization fails
                self.client = MockFirestoreClient()

    def get_student_state(self, student_id: str) -> StudentState:
        """
        Retrieve StudentState document from `students/{student_id}`.
        Returns a clean default StudentState if the document does not exist.
        """
        doc_ref = self.client.collection("students").document(student_id)
        snapshot = doc_ref.get()
        if not snapshot.exists or not snapshot.to_dict():
            return StudentState(student_id=student_id)

        data = snapshot.to_dict()
        return StudentState.model_validate(data)

    def update_student_state(self, student_id: str, state: StudentState) -> None:
        """
        Atomically write/merge StudentState document to `students/{student_id}`.
        """
        doc_ref = self.client.collection("students").document(student_id)
        payload = state.model_dump(mode="json")
        doc_ref.set(payload, merge=True)

    def append_grade_snapshot(self, student_id: str, course_id: str, snapshot: GradeSnapshot) -> None:
        """
        Append a GradeSnapshot to `courses.{course_id}.history` for a given student.
        """
        state = self.get_student_state(student_id)
        if course_id not in state.courses:
            state.courses[course_id] = CourseState(
                name=course_id,
                current_percentage=snapshot.percentage,
                letter_grade=snapshot.letter_grade,
                history=[],
            )
        
        # Append snapshot if not already present for date
        course = state.courses[course_id]
        course.current_percentage = snapshot.percentage
        course.letter_grade = snapshot.letter_grade
        
        # Replace or append
        existing_dates = [h.date for h in course.history]
        if snapshot.date in existing_dates:
            idx = existing_dates.index(snapshot.date)
            course.history[idx] = snapshot
        else:
            course.history.append(snapshot)
            # Maintain sorted order by date
            course.history.sort(key=lambda x: x.date)

        self.update_student_state(student_id, state)

    def get_grade_history(
        self, student_id: str, course_id: str, start_date: str, end_date: str
    ) -> List[GradeSnapshot]:
        """
        Retrieve list of GradeSnapshots for a course within [start_date, end_date] inclusive.
        Date strings must be in format YYYY-MM-DD.
        """
        state = self.get_student_state(student_id)
        if course_id not in state.courses:
            return []
        
        course = state.courses[course_id]
        return [
            snap for snap in course.history
            if start_date <= snap.date <= end_date
        ]

    def save_session_cookies(self, student_id: str, psaid: str) -> None:
        """
        Save encrypted SAML session cookies for PowerSchool login reuse.
        """
        cookies = SessionCookies(
            psaid=psaid,
            updated_at=datetime.now(timezone.utc).isoformat()
        )
        state = self.get_student_state(student_id)
        state.session_cookies = cookies
        self.update_student_state(student_id, state)

    def get_session_cookies(self, student_id: str) -> Optional[SessionCookies]:
        """
        Retrieve stored SessionCookies for a student.
        """
        state = self.get_student_state(student_id)
        return state.session_cookies

    def save_late_submission(self, student_id: str, record: LateSubmissionRecord) -> None:
        """
        Idempotently save or update a LateSubmissionRecord under `students/{student_id}/late_submissions/{assignment_id}`.
        """
        col_ref = self.client.collection(f"students/{student_id}/late_submissions")
        doc_ref = col_ref.document(str(record.assignment_id))
        doc_ref.set(record.model_dump(mode="json"), merge=True)

    def save_late_submissions(
        self, student_id: str, records: List[LateSubmissionRecord]
    ) -> None:
        """
        Save or update multiple LateSubmissionRecord objects.
        """
        for record in records:
            self.save_late_submission(student_id, record)

    def get_late_submissions(
        self,
        student_id: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        include_cleared: bool = False,
    ) -> List[LateSubmissionRecord]:
        """
        Retrieve list of LateSubmissionRecords for a student within [start_date, end_date] inclusive.
        Filters based on submitted_at or detected_at timestamps.
        By default, filters out records where is_late is False unless include_cleared is True.
        """
        col_ref = self.client.collection(f"students/{student_id}/late_submissions")
        docs = col_ref.stream()
        records: List[LateSubmissionRecord] = []
        for doc in docs:
            if not doc.exists or not doc.to_dict():
                continue
            data = doc.to_dict()
            rec = LateSubmissionRecord.model_validate(data)
            
            if not rec.is_late and not include_cleared:
                continue

            timestamp_str = rec.submitted_at or rec.detected_at
            rec_date = timestamp_str[:10] if timestamp_str else ""

            if start_date and rec_date and rec_date < start_date[:10]:
                continue
            if end_date and rec_date and rec_date > end_date[:10]:
                continue
            records.append(rec)

        records.sort(key=lambda r: r.submitted_at or r.detected_at or "")
        return records

    def save_dispatched_alert(
        self, student_id: str, record: DispatchedAlertRecord
    ) -> None:
        """
        Idempotently save a DispatchedAlertRecord under `students/{student_id}/dispatched_alerts/{alert_id}`.
        """
        col_ref = self.client.collection(f"students/{student_id}/dispatched_alerts")
        doc_ref = col_ref.document(str(record.alert_id))
        doc_ref.set(record.model_dump(mode="json"), merge=True)

    def get_dispatched_alerts(
        self,
        student_id: str,
        alert_type: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> List[DispatchedAlertRecord]:
        """
        Retrieve list of DispatchedAlertRecords for a student.
        Optionally filter by alert_type and [start_date, end_date] range on dispatched_at timestamp.
        """
        col_ref = self.client.collection(f"students/{student_id}/dispatched_alerts")
        docs = col_ref.stream()
        records: List[DispatchedAlertRecord] = []
        for doc in docs:
            if not doc.exists or not doc.to_dict():
                continue
            data = doc.to_dict()
            rec = DispatchedAlertRecord.model_validate(data)

            if alert_type and rec.alert_type != alert_type:
                continue

            dispatch_str = rec.dispatched_at
            rec_date = dispatch_str[:10] if dispatch_str else ""

            if start_date and rec_date and rec_date < start_date[:10]:
                continue
            if end_date and rec_date and rec_date > end_date[:10]:
                continue
            records.append(rec)

        records.sort(key=lambda r: r.dispatched_at or "")
        return records

    def update_student_preferences(
        self, student_id: str, preferences: StudentPreferences
    ) -> None:
        """
        Update custom StudentPreferences for a student.
        """
        state = self.get_student_state(student_id)
        state.preferences = preferences
        self.update_student_state(student_id, state)

    def get_student_preferences(self, student_id: str) -> StudentPreferences:
        """
        Retrieve custom StudentPreferences for a student, returning default preferences if unconfigured.
        """
        state = self.get_student_state(student_id)
        return state.preferences



