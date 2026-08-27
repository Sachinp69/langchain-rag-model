from pydantic_settings import BaseSettings,SettingsConfigDict

class Settings(BaseSettings):
    supabase_url: str
    supabase_key: str
    supabase_jwt_secret: str  # for verifying JWTs locally

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
