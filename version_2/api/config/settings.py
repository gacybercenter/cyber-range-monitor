from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    TITLE: str = 'Range Monitor v2'
    VERSION: str = '0.0.1'

    ENABLE_EVENT_LOGS: bool = True 
    
    
    SECRET_KEY: str

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str

    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_DB: int = 0

    REFRESH_TOKEN_EXP_SEC: int = 1 * 24 * 60 * 60  # 1 day
    ACCESS_TOKEN_EXP_SEC: int = 30 * 60  # 30 minutes

    DATABASE_URL: str

    DATABASE_ECHO: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        frozen=True,
        extra="ignore"
    )


app_config = Settings()  # type: ignore
