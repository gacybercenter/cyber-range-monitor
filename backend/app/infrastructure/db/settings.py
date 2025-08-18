from typing import Annotated, Final

from pydantic import Field
from pydantic_settings import SettingsConfigDict

from app.core.settings import SecretLoader, Settings, TomlLoader, TomlSettings


class SQLAlchemyOptions(TomlSettings):
    """SQLite settings for the ORM plugin."""

    pool_recycle: Annotated[
        int,
        Field(
            description='The number of seconds to recycle the connection pool.',
        ),
    ] = 3600

    # pool_timeout: Annotated[
    #     int,
    #     Field(
    #         description='The number of seconds to wait for a connection from the pool.',
    #     ),
    # ] = 30


    # pool_size: Annotated[
    #     int,
    #     Field(
    #         description='The number of connections to keep in the pool.',
    #     ),
    # ] = 10

    # max_overflow: Annotated[
    #     int,
    #     Field(
    #         description='The maximum number of connections to create beyond the pool size.'
    #     ),
    # ]
    # pool_use_lifo: Annotated[
    #     bool,
    #     Field(description='Whether to use LIFO instead of FIFO for the connection pool.')
    # ] = False

    pool_pre_ping: bool = True
    future: bool = True

    run_seed: Annotated[
        bool,
        Field(description='Whether to run the database seeding process on startup.'),
    ] = False


    expire_on_commit: Annotated[
        bool,
        Field(
            description='Whether to expire objects on commit.',
        )
    ] = False

    autoflush: Annotated[
        bool,
        Field(
            description='Whether to autoflush the session.',
        )
    ] = False

    @property
    def engine_kwargs(self) -> dict:
        return self.model_dump(
            exclude={'run_seed', 'echo', 'expire_on_commit', 'autoflush'},
        )


class DatabaseSecrets(Settings):
    model_config = SettingsConfigDict(env_prefix='DATABASE_')

    FILE_NAME: Annotated[
        str,
        Field(default=':memory:', description='The SQLite database file path.')
    ]

    TIMEOUT: Annotated[
        int,
        Field(
            description='The number of seconds to wait for a connection before timing out.',
        ),
    ] = 30

    DIRECTORY: Annotated[
        str,
        Field(description='The directory where the SQLite database file is located.'),
    ]

    ECHO: Annotated[
        bool,
        Field(description='Whether to echo SQL statements.'),
    ]

    DRIVER_NAME: str = Field(
        default='sqlite+aiosqlite',
        description='The database driver name.',
    )

    @property
    def database(self) -> str:
        return (
            f'{self.DIRECTORY}/{self.FILE_NAME}'
            if self.FILE_NAME != ':memory:'
            else self.FILE_NAME
        )


sqlalchemy_options: Final[SQLAlchemyOptions] = TomlLoader.load(
    settings_class=SQLAlchemyOptions,
    section_name='adapters.sql'
)
db_secrets: Final[DatabaseSecrets] = SecretLoader.load(
    settings_class=DatabaseSecrets
)
