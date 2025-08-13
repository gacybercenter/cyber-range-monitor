from datetime import timedelta

from pydantic import Field

from app.core.settings import TomlSettings, create_toml_settings


class AuthenticationSettings(TomlSettings):
    session_max_age_days: int = Field(
        default=1,
        description='The maximum age of a session in days',
    )

    session_idle_timeout_hours: int = Field(
        default=1,
        description='The idle timeout for a session in seconds',
    )

    @property
    def idle_timeout(self) -> int:
        """
        Returns the idle timeout in seconds.
        """
        return int(timedelta(hours=self.session_idle_timeout_hours).total_seconds())

    @property
    def session_max_age(self) -> int:
        """
        Returns the maximum age of a session in seconds.
        """
        return int(timedelta(days=self.session_max_age_days).total_seconds())


auth_settings: AuthenticationSettings = create_toml_settings(
    AuthenticationSettings,
    section_name='auth',
)
