from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Taxonomy Validator"
    env: str = "dev"
    api_v1_prefix: str = "/api/v1"

    database_url: str = "postgresql+psycopg2://postgres:postgres@db:5432/taxonomy"
    redis_url: str = "redis://redis:6379/0"

    llm_enabled: bool = False
    llm_provider: str = "openai"
    llm_model: str = "gpt-4o-mini"
    llm_api_key: str = ""

    confidence_auto_threshold: float = 0.92
    confidence_review_threshold: float = 0.65

    meta_app_id: str = ""
    meta_app_secret: str = ""
    meta_access_token: str = ""
    meta_api_version: str = "v21.0"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
