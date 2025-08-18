import uuid
from typing import Annotated

from pydantic import Field

from app.core.settings import TomlLoader, TomlSettings

SECTION_NAME = 'middleware'


class CORSConfig(TomlSettings):
    allow_origins: Annotated[
        list[str],
        Field(description='The allowed origins for CORS requests')
    ] = ['*']

    allow_methods: Annotated[
        list[str],
        Field(description='The allowed methods for CORS requests')
    ] = ['*']

    allow_headers: Annotated[
        list[str],
        Field(description='The allowed headers for CORS requests')
    ] = ['*']


    allow_credentials: Annotated[
        bool,
        Field(description='Whether to allow credentials in CORS requests'),
    ] = True


class CorrelationIdConfig(TomlSettings):
    header_name: str = Field(
        default='X-Request-ID',
        description='The name of the header used for correlation IDs',
    )

    update_request_header: bool = Field(
        default=True,
        description='Whether to update the request header with the correlation ID',
    )


    def id_factory(self) -> uuid.UUID:
        """
        Generates a new UUID for the correlation ID.

        Returns
        -------
        uuid.UUID
            A new UUID instance.
        """
        return uuid.uuid4()


class MiddlewareSetttings(TomlSettings):
    cors: CORSConfig = CORSConfig()
    correlation_id: CorrelationIdConfig

    allowed_hosts: list[str] | None = Field(
        default=None,
        description='List of allowed hosts for the application. If None, all hosts are allowed.',
    )


middleware_settings: MiddlewareSetttings = TomlLoader.load(
    MiddlewareSetttings,
    section_name=SECTION_NAME,
)
