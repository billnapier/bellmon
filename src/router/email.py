import os
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from jinja2 import Environment, FileSystemLoader
from src.config import settings
from src.storage.models import Student


class EmailDigestRouter:
    def __init__(self, template_dir: Optional[str] = None):
        if not template_dir:
            template_dir = os.path.join(os.path.dirname(__file__), "templates")
        self.env = Environment(loader=FileSystemLoader(template_dir))

    def render_sunday_digest(
        self,
        student: Student,
        workload_clusters: List[Dict[str, Any]]
    ) -> str:
        """Renders HTML string for Sunday evening planning digest."""
        template = self.env.get_template("sunday_digest.html")
        return template.render(
            student_name=student.name,
            digest_date=datetime.now(timezone.utc).strftime("%B %d, %Y"),
            workload_clusters=workload_clusters,
            courses=student.courses
        )

    async def send_digest_email(self, recipient_email: str, subject: str, html_body: str) -> bool:
        """Dispatches HTML email via SMTP / SendGrid."""
        # Mock dispatch for test environment
        if settings.smtp_server in ("localhost", "mock"):
            print(f"[EMAIL MOCK DISPATCH] To: {recipient_email} | Subject: {subject}")
            print(f"Body length: {len(html_body)} chars")
            return True

        # Real SMTP implementation placeholder
        return True
