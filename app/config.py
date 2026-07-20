"""
App configuration — reads from .env file using pydantic-settings.
All env vars are validated and typed here; nothing else reads os.environ directly.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # MySQL credentials (from .env)
    mysql_host: str = "localhost"
    mysql_port: int = 3306
    mysql_user: str = "root"
    mysql_password: str = ""
    mysql_database: str = ""

    # App
    app_env: str = "development"
    debug: bool = True
    auth_secret_key: str = "change-this-secret-in-production"
    auth_token_expire_hours: int = 24
    app_url: str = "http://localhost:3000"

    # SMTP Email Settings (optional, configured via .env)
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from_email: str = ""
    smtp_use_tls: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    @property
    def database_url(self) -> str:
        """Build MySQL connection URL from individual credentials."""
        return (
            f"mysql+pymysql://{self.mysql_user}:{self.mysql_password}"
            f"@{self.mysql_host}:{self.mysql_port}/{self.mysql_database}"
        )


# Single shared instance — import this everywhere
settings = Settings()
