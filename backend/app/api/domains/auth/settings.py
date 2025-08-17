from datetime import timedelta

from pydantic import Field

from app.core.settings import TomlSettings, create_toml_settings


class AuthenticationSettings(TomlSettings):
    remember_me_max_age_days: int = Field(
        default=1,
        description='The maximum age of a session when remember me is enabled',
    )

    redis_prefix: str = Field(
        default='auth:',
        description='The prefix for session keys in Redis',
    )

    base_max_age_hours: int = Field(
        default=3,
        description='The base maximum age of a session in hours',
    )

    idle_timeout_mins: int = Field(
        default=90,
        description='The idle timeout for a session in minutes',
    )

    header_name: str = Field(
        default='Authorization',
        description='The name of the HTTP header used to get the session ID.',
    )



    @property
    def idle_timeout(self) -> int:
        """
        Returns the idle timeout in seconds.
        """
        return int(timedelta(minutes=self.idle_timeout_mins).total_seconds())

    @property
    def base_max_age(self) -> int:
        """
        Returns the maximum age of a session in seconds.
        """
        return int(timedelta(days=self.remember_me_max_age_days).total_seconds())

    @property
    def remember_me_max_age(self) -> int:
        """
        Returns the maximum age of a session when remember me is enabled in seconds.
        """
        return int(timedelta(days=self.remember_me_max_age_days).total_seconds())


auth_settings: AuthenticationSettings = create_toml_settings(
    AuthenticationSettings,
    section_name='auth',
)
