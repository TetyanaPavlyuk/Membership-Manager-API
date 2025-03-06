from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    BACKEND_HOST: str = "0.0.0.0"
    BACKEND_PORT: int = 8000
    ORIGINS: str = "http://localhost:3000"

    model_config = SettingsConfigDict(env_file=".env")

    @property
    def parse_origins(self):
        return [origin.strip() for origin in self.ORIGINS.split(",")]


settings = Settings()
