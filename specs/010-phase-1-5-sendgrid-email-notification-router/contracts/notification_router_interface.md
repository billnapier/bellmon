# Notification Router & SendGrid Interface Contract

## 1. `NotificationRenderer`

```python
class NotificationRenderer:
    def compile_p0_email(
        self,
        student_name: str,
        missing_work: List[Any] = [],
        grade_drops: List[Any] = [],
        attendance_anomalies: List[Any] = [],
    ) -> Tuple[str, str]:
        """
        Compiles responsive HTML and plaintext fallback bodies for aggregated P0 alerts.
        Returns: (html_body, text_fallback)
        """
        ...
```

## 2. `SendGridClient`

```python
class SendGridClient:
    def __init__(self, api_key: Optional[str] = None, from_email: str = "alerts@bellmon.app"):
        ...

    def send_email(self, payload: EmailPayload) -> DispatchResult:
        """
        Sends email via SendGrid Web API v3 or simulates delivery if dry-run / unconfigured.
        """
        ...
```

## 3. `NotificationRouter`

```python
class NotificationRouter:
    def __init__(self, sendgrid_client: Optional[SendGridClient] = None, dry_run: bool = False):
        ...

    def dispatch_alerts(
        self,
        recipient_email: str,
        student_name: str,
        missing_work: List[Any] = [],
        grade_drops: List[Any] = [],
        attendance_anomalies: List[Any] = [],
    ) -> DispatchResult:
        """
        Aggregates pending P0 alerts, renders responsive HTML body, and dispatches via SendGridClient.
        """
        ...
```
