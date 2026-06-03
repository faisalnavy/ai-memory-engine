from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # App
    APP_NAME: str = "AI Memory Engine SaaS"
    VERSION:  str = "1.0.0"
    DEBUG:    bool = False

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:password@localhost/memory_engine"

    # Redis
    REDIS_URL: str = "redis://localhost:6379"

    # Auth
    SECRET_KEY: str = "change-me-in-production-use-32-char-random-string"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    ALGORITHM: str = "HS256"

    # AWS S3 (for storing .memory/ databases in cloud)
    AWS_ACCESS_KEY_ID:     str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_REGION:            str = "ap-south-1"
    S3_BUCKET:             str = "ai-memory-engine"

    # Stripe
    STRIPE_SECRET_KEY:      str = ""
    STRIPE_WEBHOOK_SECRET:  str = ""

    # Plans
    STRIPE_PRICE_PRO:       str = ""  # monthly price ID
    STRIPE_PRICE_TEAM:      str = ""

    # CORS
    ALLOWED_ORIGINS: list[str] = ["http://localhost:3000", "https://your-domain.com"]

    class Config:
        env_file = ".env"


settings = Settings()
