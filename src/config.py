import os
from pydantic import BaseModel, Field


class Settings(BaseModel):
    # Canvas LMS
    canvas_base_url: str = Field(default_factory=lambda: os.getenv("CANVAS_BASE_URL", "https://canvas.bellarmine.org"))
    canvas_api_token: str = Field(default_factory=lambda: os.getenv("CANVAS_API_TOKEN", "mock_canvas_token"))

    # PowerSchool SIS
    powerschool_base_url: str = Field(default_factory=lambda: os.getenv("POWERSCHOOL_BASE_URL", "https://powerschool.bellarmine.org"))
    powerschool_username: str = Field(default_factory=lambda: os.getenv("POWERSCHOOL_USERNAME", "mock_user"))
    powerschool_password: str = Field(default_factory=lambda: os.getenv("POWERSCHOOL_PASSWORD", "mock_pass"))

    # Storage
    firestore_project_id: str = Field(default_factory=lambda: os.getenv("FIRESTORE_PROJECT_ID", "bellmon-dev"))
    use_local_storage: bool = Field(default_factory=lambda: os.getenv("USE_LOCAL_STORAGE", "true").lower() == "true")

    # Notifications
    pushover_user_key: str = Field(default_factory=lambda: os.getenv("PUSHOVER_USER_KEY", ""))
    pushover_app_token: str = Field(default_factory=lambda: os.getenv("PUSHOVER_APP_TOKEN", ""))
    smtp_server: str = Field(default_factory=lambda: os.getenv("SMTP_SERVER", "localhost"))
    smtp_port: int = Field(default_factory=lambda: int(os.getenv("SMTP_PORT", "587")))
    smtp_user: str = Field(default_factory=lambda: os.getenv("SMTP_USER", ""))
    smtp_password: str = Field(default_factory=lambda: os.getenv("SMTP_PASSWORD", ""))

    # Sentinel Rules
    grace_period_hours: float = Field(default=36.0)
    grade_velocity_drop_threshold: float = Field(default=4.0)
    workload_clumping_window_hours: float = Field(default=48.0)
    workload_clumping_min_assessments: int = Field(default=2)


settings = Settings()
