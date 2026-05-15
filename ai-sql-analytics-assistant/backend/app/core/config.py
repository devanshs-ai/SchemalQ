from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "SchemaIQ"
    APP_ENV: str  # "development" | "production" — required, no default

    # PostgreSQL
    DATABASE_URL: str  # required — e.g. postgresql+asyncpg://user:pass@host:5432/db

    # Redis
    REDIS_HOST: str  # required
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

    # Groq LLM
    GROQ_API_KEY: str  # required
    GROQ_MODEL: str = "llama-3.3-70b-versatile"

    # Query cache
    CACHE_TTL: int = 300  # seconds

    # CORS
    ALLOWED_ORIGINS: str = "*"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
