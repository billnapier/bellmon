import json
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from src.config import settings


class AlertRecord(BaseModel):
    alert_id: str
    student_id: str
    assignment_id: Optional[str] = None
    alert_type: str  # MISSING_WORK, VELOCITY_DROP, WORKLOAD_CLUMPING, ATTENDANCE
    channel: str  # PUSHOVER, NTFY, EMAIL
    dispatched_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    payload: Dict[str, Any] = Field(default_factory=dict)


class AlertLedger:
    def __init__(self):
        self._records: Dict[str, AlertRecord] = {}

    def is_already_alerted(self, alert_id: str) -> bool:
        return alert_id in self._records

    def record_alert(self, alert: AlertRecord) -> None:
        self._records[alert.alert_id] = alert

    def clear(self) -> None:
        self._records.clear()
