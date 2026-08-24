"""
Resend REST API Delivery Client with Dry-Run Local Logging Fallback.
"""

import os
import json
import uuid
import logging
import urllib.request
import urllib.error
from typing import Optional

from src.notifications.models import EmailPayload, DispatchResult

logger = logging.getLogger("bellmon.notifications.resend")


class ResendClient:
    """Delivers email notifications via Resend REST API or simulates delivery in dry-run mode."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        from_email: str = "Bellmon Academic Sentinel <alerts@bellmon.dev>",
        dry_run: Optional[bool] = None,
    ):
        """
        Initializes the Resend client.

        Args:
            api_key: Resend API key (defaults to RESEND_API_KEY env var).
            from_email: Sender email address or name format.
            dry_run: Forced dry-run flag (defaults to DRY_RUN env var or True if api_key is missing).
        """
        if not api_key and not os.getenv("RESEND_API_KEY") and os.path.exists(".env"):
            try:
                with open(".env", "r") as f:
                    for line in f:
                        line_str = line.strip()
                        if line_str.startswith("RESEND_API_KEY="):
                            api_key = line_str.split("=", 1)[1].strip('"\'')
                        elif line_str.startswith("DRY_RUN=") and dry_run is None:
                            val = line_str.split("=", 1)[1].strip('"\'').lower()
                            dry_run = val in ("true", "1", "yes")
            except Exception:
                pass

        self.api_key = api_key or os.getenv("RESEND_API_KEY")
        self.from_email = from_email

        env_dry_run = os.getenv("DRY_RUN", "false").lower() in ("true", "1", "yes")
        if dry_run is not None:
            self.dry_run = dry_run
        else:
            self.dry_run = env_dry_run or not bool(self.api_key)

    def send_email(self, payload: EmailPayload) -> DispatchResult:
        """
        Sends an email payload via Resend REST API or simulates sending if in dry-run mode.

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
            print("--- [DRY-RUN EMAIL SIMULATION] ---")
            print(f"To: {payload.recipient_email}")
            print(f"Subject: {payload.subject}")
            print(f"Body (Text Snippet):\n{payload.text_fallback[:200]}...")
            print("----------------------------------")

            return DispatchResult(
                success=True,
                message_id=simulated_id,
                recipient=payload.recipient_email,
                dry_run=True,
            )

        url = "https://api.resend.com/emails"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "Bellmon-Academic-Sentinel/1.0",
        }

        body_data = {
            "from": self.from_email,
            "to": [payload.recipient_email],
            "subject": payload.subject,
            "html": payload.html_body,
            "text": payload.text_fallback,
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
                raw_resp = response.read().decode("utf-8")
                try:
                    resp_json = json.loads(raw_resp) if raw_resp else {}
                    msg_id = resp_json.get("id") or f"resend-{uuid.uuid4()}"
                except json.JSONDecodeError:
                    msg_id = f"resend-{uuid.uuid4()}"

                if status_code in (200, 201, 202):
                    logger.info(f"Successfully dispatched email via Resend. Message ID: {msg_id}")
                    return DispatchResult(
                        success=True,
                        message_id=msg_id,
                        recipient=payload.recipient_email,
                        dry_run=False,
                    )
                else:
                    error_msg = f"Resend API returned status {status_code}"
                    logger.error(error_msg)
                    return DispatchResult(
                        success=False,
                        recipient=payload.recipient_email,
                        error_message=error_msg,
                        dry_run=False,
                    )
        except urllib.error.HTTPError as err:
            error_body = err.read().decode("utf-8", errors="ignore")
            error_msg = f"Resend HTTP {err.code}: {error_body or err.reason}"
            logger.error(f"Failed to dispatch email via Resend: {error_msg}")
            return DispatchResult(
                success=False,
                recipient=payload.recipient_email,
                error_message=error_msg,
                dry_run=False,
            )
        except Exception as err:
            error_msg = f"Resend request exception: {err}"
            logger.error(error_msg)
            return DispatchResult(
                success=False,
                recipient=payload.recipient_email,
                error_message=error_msg,
                dry_run=False,
            )
