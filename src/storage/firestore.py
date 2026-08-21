import json
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from src.config import settings
from src.storage.models import Student, CourseSnapshot


class LocalStorageClient:
    """In-memory / local storage client for offline development & tests."""

    def __init__(self):
        self._students: Dict[str, Dict[str, Any]] = {}
        self._history: Dict[str, list] = {}

    def get_student_snapshot(self, student_id: str) -> Optional[Student]:
        data = self._students.get(student_id)
        if not data:
            return None
        return Student.model_validate(data)

    def save_student_snapshot(self, student: Student) -> None:
        raw_data = json.loads(student.model_dump_json())
        self._students[student.student_id] = raw_data
        
        if student.student_id not in self._history:
            self._history[student.student_id] = []
        self._history[student.student_id].append(raw_data)

    def get_historical_snapshots(self, student_id: str, limit: int = 14) -> list:
        history = self._history.get(student_id, [])
        return history[-limit:]


class FirestoreStore:
    def __init__(self):
        self.use_local = settings.use_local_storage
        if self.use_local:
            self.client = LocalStorageClient()
        else:
            from google.cloud import firestore
            self.client = firestore.Client(project=settings.firestore_project_id)

    def load_student(self, student_id: str) -> Optional[Student]:
        if self.use_local:
            return self.client.get_student_snapshot(student_id)
        
        doc_ref = self.client.collection("students").document(student_id)
        doc = doc_ref.get()
        if not doc.exists:
            return None
        return Student.model_validate(doc.to_dict())

    def save_student(self, student: Student) -> None:
        if self.use_local:
            self.client.save_student_snapshot(student)
            return

        doc_ref = self.client.collection("students").document(student.student_id)
        raw_data = json.loads(student.model_dump_json())
        doc_ref.set(raw_data, merge=True)
