import httpx
from typing import List, Dict, Any
from src.config import settings
from src.storage.models import TrackedAssignment, SubmissionType, AssignmentState


class CanvasHarvester:
    def __init__(self, base_url: str = None, token: str = None):
        self.base_url = (base_url or settings.canvas_base_url).rstrip("/")
        self.token = token or settings.canvas_api_token

    async def fetch_missing_assignments(self, student_id: str) -> List[TrackedAssignment]:
        """Fetch missing assignments from Canvas REST API."""
        headers = {"Authorization": f"Bearer {self.token}"}
        url = f"{self.base_url}/api/v1/users/self/missing_submissions"

        # Mock fallback for test environment
        if self.token.startswith("mock"):
            return self._get_mock_missing_assignments()

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, timeout=10.0)
            if response.status_code != 200:
                return []
            data = response.json()
            return self._parse_assignments(data)

    def _parse_assignments(self, data: List[Dict[str, Any]]) -> List[TrackedAssignment]:
        assignments = []
        for item in data:
            sub_type = SubmissionType.ONLINE_UPLOAD
            raw_sub_types = item.get("submission_types", [])
            if "online_upload" in raw_sub_types:
                sub_type = SubmissionType.ONLINE_UPLOAD
            elif "on_paper" in raw_sub_types:
                sub_type = SubmissionType.PAPER

            assignments.append(
                TrackedAssignment(
                    assignment_id=str(item.get("id")),
                    course_id=str(item.get("course_id")),
                    title=item.get("name", "Untitled Assignment"),
                    due_at=item.get("due_at"),
                    submission_type=sub_type,
                    points_possible=float(item.get("points_possible", 0.0)),
                    canvas_missing=True,
                    state=AssignmentState.NEW
                )
            )
        return assignments

    def _get_mock_missing_assignments(self) -> List[TrackedAssignment]:
        return [
            TrackedAssignment(
                assignment_id="canvas_101",
                course_id="course_math_10",
                title="Chapter 4 Worksheet",
                submission_type=SubmissionType.ONLINE_UPLOAD,
                points_possible=50.0,
                canvas_missing=True,
                state=AssignmentState.NEW
            )
        ]
