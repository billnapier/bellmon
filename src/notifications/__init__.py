"""
Bellmon Notification Package.

Provides responsive HTML email rendering, Resend REST API delivery,
and aggregated P0 alert routing.
"""

from src.notifications.models import EmailPayload, DispatchResult
from src.notifications.renderer import NotificationRenderer
from src.notifications.resend import ResendClient
from src.notifications.router import NotificationRouter
from src.notifications.digest import (
    SundayDigestPayload,
    SundayDigestRenderer,
    SundayDigestRouter,
)
from src.notifications.heartbeat import HeartbeatBriefingGenerator
from src.notifications.models import (
    HeartbeatPayload,
    GraceWatchlistItem,
    PortalIngestionRecord,
    DailyAttendanceSummary,
    AttendancePeriodRecord,
)

__all__ = [
    "EmailPayload",
    "DispatchResult",
    "NotificationRenderer",
    "ResendClient",
    "NotificationRouter",
    "SundayDigestPayload",
    "SundayDigestRenderer",
    "SundayDigestRouter",
    "HeartbeatBriefingGenerator",
    "HeartbeatPayload",
    "GraceWatchlistItem",
    "PortalIngestionRecord",
    "DailyAttendanceSummary",
    "AttendancePeriodRecord",
]

