import httpx
from typing import Dict, Any, Optional
from src.config import settings
from src.storage.ledger import AlertRecord, AlertLedger


class PushRouter:
    def __init__(self, ledger: Optional[AlertLedger] = None):
        self.user_key = settings.pushover_user_key
        self.app_token = settings.pushover_app_token
        self.ledger = ledger or AlertLedger()

    async def send_p0_alert(
        self,
        alert_id: str,
        student_id: str,
        title: str,
        message: str,
        alert_type: str = "MISSING_WORK",
        assignment_id: Optional[str] = None
    ) -> bool:
        """Dispatch P0 alert via Pushover/NTFY with idempotency check."""
        if self.ledger.is_already_alerted(alert_id):
            return False  # Suppress duplicate alert

        payload = {
            "token": self.app_token,
            "user": self.user_key,
            "title": title,
            "message": message,
            "priority": 1  # High priority P0
        }

        # Mock dispatch if tokens not configured
        if not self.user_key or not self.app_token:
            print(f"[PUSH MOCK DISPATCH] Title: {title} | Message: {message}")
            dispatched = True
        else:
            async with httpx.AsyncClient() as client:
                res = await client.post("https://api.pushover.net/1/messages.json", data=payload, timeout=5.0)
                dispatched = res.status_code == 200

        if dispatched:
            record = AlertRecord(
                alert_id=alert_id,
                student_id=student_id,
                assignment_id=assignment_id,
                alert_type=alert_type,
                channel="PUSHOVER",
                payload=payload
            )
            self.ledger.record_alert(record)
        return dispatched
