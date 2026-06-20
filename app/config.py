from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Database
    database_url: str = "postgresql+psycopg://aiops:aiops@db:5432/aiops"

    # Redis
    redis_url: str = "redis://redis:6379/0"

    # LLM
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    llm_provider: str = "openai"  # openai | anthropic
    llm_model: str = "gpt-4o-mini"

    # App
    log_level: str = "INFO"
    dedup_ttl_seconds: int = 300

    # Notifications
    slack_webhook_url: str = ""

    # Server
    api_host: str = "0.0.0.0"
    api_port: int = 8000


settings = Settings()
