from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg://fincore:fincore@localhost:5432/fincore"
    jwt_secret: str = ""
    jwt_exp_minutes: int = 30
    redis_url: str = "redis://localhost:6379/0"
    admin_email: str = ""
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
