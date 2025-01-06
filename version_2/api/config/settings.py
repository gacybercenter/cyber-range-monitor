from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    TITLE: str = 'Range Monitor v2'
    VERSION: str = '0.0.1'

    SECRET_KEY: str
    DATABASE_URL: str
    DATABASE_ECHO: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        frozen=True,
        extra="ignore"
    )


app_config = Settings()  # type: ignore
