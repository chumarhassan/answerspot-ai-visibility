"""Central configuration, loaded from environment / .env.

All secrets live here and are read server-side only — never sent to the frontend (§8).
"""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Database
    database_url: str = "sqlite:///./answerspot.db"

    # Auth
    jwt_secret: str = "change-me-to-a-long-random-secret"
    jwt_expires_minutes: int = 60 * 24 * 7  # 7 days
    jwt_algorithm: str = "HS256"

    # Gemini (only tracked platform for MVP — free tier)
    gemini_api_key: str = ""
    gemini_model: str = "gemini-flash-latest"

    # Google OAuth
    google_oauth_client_id: str = ""
    google_oauth_client_secret: str = ""
    google_oauth_redirect_uri: str = "http://localhost:5173/auth/google/callback"

    # Stripe (test mode by default)
    stripe_secret_key: str = ""
    stripe_webhook_secret: str = ""
    stripe_starter_price_id: str = ""
    stripe_pro_price_id: str = ""

    # Frontend
    frontend_url: str = "http://localhost:5173"

    @property
    def gemini_configured(self) -> bool:
        return bool(self.gemini_api_key)

    @property
    def stripe_configured(self) -> bool:
        return bool(self.stripe_secret_key)

    @property
    def google_oauth_configured(self) -> bool:
        return bool(self.google_oauth_client_id and self.google_oauth_client_secret)


@lru_cache
def get_settings() -> Settings:
    return Settings()
