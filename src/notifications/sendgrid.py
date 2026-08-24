"""
SendGrid Web API v3 Delivery Client with Dry-Run Local Logging Fallback.
"""

import os
import json
import uuid
import logging
import urllib.request
import urllib.error
from typing import Optional

from src.notifications.models import EmailPayload, DispatchResult

logger = logging.getLogger("bellmon.notifications.sendgrid")


class SendGridClient:
    """Delivers email notifications via SendGrid Web API v3 or simulates delivery in dry-run mode."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        from_email: str = "alerts@bellmon.app",
        dry_run: Optional[bool] = None,
    ):
        """
        Initializes the SendGrid client.

        Args:
            api_key: SendGrid Web API v3 key (defaults to SENDGRID_API_KEY env var).
            from_email: Sender email address.
            dry_run: Forced dry-run flag (defaults to DRY_RUN env var or True if api_key is missing).
        """
        self.api_key = api_key or os.getenv("SENDGRID_API_KEY")
        self.from_email = from_email

        env_dry_run = os.getenv("DRY_RUN", "false").lower() in ("true", "1", "yes")
        if dry_run is not None:
            self.dry_run = dry_run
        else:
            self.dry_run = env_dry_run or not bool(self.api_key)

    def send_email(self, payload: EmailPayload) -> DispatchResult:
        """
        Sends an email payload via SendGrid REST API or simulates sending if in dry-run mode.

        Args:
            payload: EmailPayload object containing recipient, subject, and bodies.

        Returns:
            DispatchResult tracking success status and message ID.
        """
        if self.dry_run or not self.api_key:
            simulated_id = f"simulated-{uuid.uuid4()}"
            logger.info(
                f"[DRY-RUN] Simulating email delivery to {payload.recipient_email}. "
                f"Subject: '{payload.subject}'. Message ID: {simulated_id}"
            )
            print(f"--- [DRY-RUN EMAIL SIMULATION] ---")
            print(f"To: {payload.recipient_email}")
            print(f"Subject: {payload.subject}")
            print(f"Body (Text Snippet):\n{payload.text_fallback[:200]}...")
            print(f"----------------------------------")

            return DispatchResult(
                success=True,
                message_id=simulated_id,
                recipient=payload.recipient_email,
                dry_run=True,
            )

        url = "https://api.sendgrid.com/v3/mail/send"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        body_data = {
            "personalizations": [
                {
                    "to": [{"email": payload.recipient_email}]
                }
            ],
            "from": {"email": self.from_email, "name": "Bellmon Academic Sentinel"},
            "subject": payload.subject,
            "content": [
                {"type": "text/plain", "value": payload.text_fallback},
                {"type": "text/html", "value": payload.html_body},
            ],
        }

        req = urllib.request.Request(
            url,
            data=json.dumps(body_data).encode("utf-8"),
            headers=headers,
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                status_code = response.getcode()
                resp_headers = dict(response.info())
                msg_id = resp_headers.get("X-Message-Id") or f"sg-{uuid.uuid4()}"

                if status_code in (200, 201, 202):
                    logger.info(f"Successfully dispatched email via SendGrid. Message ID: {msg_id}")
                    return DispatchResult(
                        success=True,
                        message_id=msg_id,
                        recipient=payload.recipient_email,
                        dry_run=False,
                    )
                else:
                    error_msg = f"SendGrid API returned status {status_code}"
                    logger.error(error_msg)
                    return DispatchResult(
                        success=False,
                        recipient=payload.recipient_email,
                        error_message=error_msg,
                        dry_run=False,
                    )
        except urllib.error.HTTPError as err:
            error_body = err.read().decode("utf-8", errors="ignore")
            error_msg = f"SendGrid HTTP {err.code}: {error_body or err.reason}"
            logger.error(f"Failed to dispatch email via SendGrid: {error_msg}")
            return DispatchResult(
                success=False,
                recipient=payload.recipient_email,
                error_message=error_msg,
                dry_run=False,
            )
        except Exception as err:
            error_msg = f"SendGrid request exception: {err}"
            logger.error(error_msg)
            return DispatchResult(
                success=False,
                recipient=payload.recipient_email,
                error_message=error_msg,
                dry_run=False,
            )
