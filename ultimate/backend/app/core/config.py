from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Robust configuration loader managing multi-tenant execution parameters.
    Binds directly to environment variables with enforced type validation.
    """
    PROJECT_NAME: str = "Real Estate Lead Platform"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"
    
    # Database Integration Layer
    DATABASE_URL: str = "postgresql://postgres:postgres@db:5432/leaddb"
    
    # Serverless Cache & PubSub Layer
    REDIS_URL: str = "redis://:securepassword@redis:6379/0"
    
    # ----------------------------------------------------------------------
    # RUNTIME BUDGET SAFETY CONTROLS
    # ----------------------------------------------------------------------
    # Hard baseline cost parameters dictating the absolute limits of compute
    MAX_DAILY_BUDGET_AED: float = 1.00
    
    # Simulated Free Tier cost metrics tracking utilization fractions
    COST_PER_DATABASE_WRITE: float = 0.00
    COST_PER_API_REQUEST: float = 0.000002
    
    # Zero-Touch Rate Limiting
    RATE_LIMIT_MAX_REQUESTS: int = 100
    RATE_LIMIT_WINDOW_SECONDS: int = 60

    # Config enforcement instructing Pydantic to read from local .env if available
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore"
    )


# Instantiate the global singleton settings object
settings = Settings()
