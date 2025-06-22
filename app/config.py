from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """
    Application settings.
    """
    # Simulated Market Generator
    message_rate_per_second: int = 1000

    # Data Ingestion Buffer
    buffer_size: int = 1000

    # Database
    db_url: str = "sqlite:///./trading_metrics.db"

    class Config:
        env_file = ".env"

settings = Settings()