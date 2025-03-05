from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    BACKEND_HOST: str = "0.0.0.0"
    BACKEND_PORT: int = 8000

    ORIGINS: str = "http://localhost:3000"

    # PostgreSQL
    POSTGRES_HOST: str = "postgres_db"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str = ""

    # Redis
    REDIS_HOST: str = "redis_db"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

    model_config = SettingsConfigDict(env_file=".env")

    @property
    def parse_origins(self):
        return [origin.strip() for origin in self.ORIGINS.split(",")]


settings = Settings()
