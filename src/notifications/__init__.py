"""
Bellmon Notification Package.

Provides responsive HTML email rendering, SendGrid REST API delivery,
and aggregated P0 alert routing.
"""

from src.notifications.models import EmailPayload, DispatchResult
from src.notifications.renderer import NotificationRenderer
from src.notifications.sendgrid import SendGridClient
from src.notifications.router import NotificationRouter

__all__ = [
    "EmailPayload",
    "DispatchResult",
    "NotificationRenderer",
    "SendGridClient",
    "NotificationRouter",
]
