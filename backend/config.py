from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
DEFAULT_JWT_SECRET = "change-me-to-a-long-random-secret"
class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    environment: str = "development"
    database_url: str = "sqlite:///./answerspot.db"
    jwt_secret: str = DEFAULT_JWT_SECRET
    jwt_expires_minutes: int = 60 * 24 * 7
    jwt_algorithm: str = "HS256"
    cors_origins: str = ""
    gemini_api_key: str = ""
    gemini_model: str = "gemini-flash-latest"
    openrouter_api_key: str = ""
    openrouter_model: str = "openrouter/auto:free"
    groq_api_key: str = ""
    groq_model: str = "llama-3.3-70b-versatile"
    resend_api_key: str = ""
    resend_from_email: str = "Answerspot <onboarding@resend.dev>"
    stripe_secret_key: str = ""
    stripe_webhook_secret: str = ""
    stripe_starter_price_id: str = ""
    stripe_pro_price_id: str = ""
    frontend_url: str = "http://localhost:5173"
    @property
    def gemini_configured(self) -> bool:
        return bool(self.gemini_api_key)
    @property
    def stripe_configured(self) -> bool:
        return bool(self.stripe_secret_key)
    @property
    def openrouter_configured(self) -> bool:
        return bool(self.openrouter_api_key)
    @property
    def groq_configured(self) -> bool:
        return bool(self.groq_api_key)
    @property
    def resend_configured(self) -> bool:
        return bool(self.resend_api_key)
    @property
    def is_production(self) -> bool:
        return self.environment.strip().lower() in {"production", "prod"}
    @property
    def jwt_secret_is_insecure(self) -> bool:
        return self.jwt_secret == DEFAULT_JWT_SECRET or len(self.jwt_secret) < 32
    @property
    def allowed_origins(self) -> list[str]:
        origins = [self.frontend_url]
        if self.cors_origins:
            origins += [o.strip() for o in self.cors_origins.split(",") if o.strip()]
        if not self.is_production:
            origins += ["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:5174", "http://127.0.0.1:5174"]
        return list(dict.fromkeys(o for o in origins if o))
@lru_cache
def get_settings() -> Settings:
    return Settings()