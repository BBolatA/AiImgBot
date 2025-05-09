from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    tg_token: str
    backend_url: str
    base_url: str
    bot_internal_token: str

    model_config = SettingsConfigDict(env_file='.env', extra='ignore')


settings = Settings()
