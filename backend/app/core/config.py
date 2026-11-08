"""Environment-backed application settings."""

from functools import lru_cache

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "CampusLend"
    app_env: str = "dev"
    log_level: str = "INFO"
    api_prefix: str = "/api/v1"
    secret_key: str = "change-me-dev-only-not-for-production"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 14
    cookie_secure: bool = False
    cookie_samesite: str = "lax"
    cors_origins: list[str] = ["http://localhost:5173"]
    database_url: str = "sqlite:///./campuslend.db"
    allowed_email_domains: list[str] = ["smail.iitm.ac.in"]
    admin_emails: list[str] = []
    otp_ttl_minutes: int = 10
    otp_max_attempts: int = 5
    otp_requests_per_hour: int = 5
    mail_backend: str = "console"
    mail_from: str = "no-reply@example.edu"
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_starttls: bool = True
    handover_code_ttl_minutes: int = 10
    code_max_attempts: int = 5
    return_claim_auto_accept_hours: int = 24
    loan_auto_close_hours: int = 48
    agreement_version: int = 1
    max_open_requests_member: int = 2
    max_open_requests_trusted: int = 5
    max_active_loans_member: int = 1
    max_active_loans_trusted: int = 3
    new_borrower_low_value_loans: int = 3
    trust_start: int = 50
    trust_on_time: int = 4
    trust_late: int = -8
    trust_report_upheld: int = -15
    trust_dispute_lost: int = -25
    trust_dispute_won: int = 5
    trust_tier_restricted_below: int = 30
    trust_tier_trusted_from: int = 70
    rate_limit_auth_per_min: int = 10
    rate_limit_write_per_min: int = 30
    rate_limit_read_per_min: int = 120
    upload_dir: str = "./uploads"
    max_upload_mb: int = 5

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore", enable_decoding=False
    )

    @field_validator("cors_origins", "allowed_email_domains", "admin_emails", mode="before")
    @classmethod
    def split_csv(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, str):
            return [part.strip() for part in value.split(",") if part.strip()]
        return value

    @field_validator("allowed_email_domains", "admin_emails", mode="after")
    @classmethod
    def normalise_values(cls, value: list[str]) -> list[str]:
        return [item.lower() for item in value]

    @model_validator(mode="after")
    def validate_production(self) -> "Settings":
        if self.app_env == "prod":
            if len(self.secret_key) < 32 or self.secret_key == "change-me-dev-only-not-for-production":
                raise ValueError("SECRET_KEY must be a strong non-default value in prod")
            if "*" in self.cors_origins:
                raise ValueError("CORS_ORIGINS cannot contain '*' in prod")
            if self.mail_backend == "console":
                raise ValueError("MAIL_BACKEND=console is not allowed in prod")
            if not self.cookie_secure:
                raise ValueError("COOKIE_SECURE must be true in prod")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
