import asyncio
import os
import typer

from rich.table import Table

from contextlib import asynccontextmanager

from pathlib import Path

from typing import Any, AsyncGenerator, List


from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.schema import CreateTable

from app.core.controller import CRUDController
import app.db.seed as seed
from app.db.core import connect_db, engine, get_session

from app.misc.model_map import get_model_map
from . import cli_console

db_app = typer.Typer()


CREATE_CMD_HELP = (
    'Creates the database and seeds the database with the default seed data.'
)
RESET_CMD_HELP = (
    'Reinitializes the database by dropping all tables and reseeding the database.'
    '\n\tNOTE: this will delete all data in the database.'
)
NAMES_CMD_HELP = 'Shows the CLI names of the database tables.'
SHOW_CMD_HELP = 'Shows a table in the database and shows 10 rows. Usage "peek <model_name>".'
TABLES_CMD_HELP = 'Shows information about the tables in the database.'


@asynccontextmanager
async def command_wrapper() -> AsyncGenerator[AsyncSession, None]:
    await connect_db()
    async with get_session() as session:
        yield session


class DBCommandUtils:
    @staticmethod
    async def model_data(model_type: DeclarativeBase, prefix: str, session: AsyncSession) -> tuple:
        service = DBCommandUtils.create_service(model_type)
        table_name = service.model.__tablename__  # type: ignore
        sql_schema = str(CreateTable(model_type.__table__))  # type: ignore
        size = await service.size(session)  # type: ignore

        return (table_name, prefix, sql_schema, size)

    @staticmethod
    def get_model_data(table: Table) -> None:
        asyncio.run(DBCommandUtils.get_model_row(table))

    @staticmethod
    async def get_model_row(table: Table) -> None:
        from app.extensions.model_map import get_model_map
        model_map = get_model_map()
        async with command_wrapper() as session:
            for model in model_map:
                table_name, prefix, sql_schema, size = await DBCommandUtils.model_data(
                    model_map[model], model, session
                )
                table.add_row(table_name, prefix, sql_schema, str(size))

    @staticmethod
    def seed_db() -> None:
        cli_console.header('bold green', 'database_seeder')
        asyncio.run(seed.default_seed())
        cli_console.header('bold blue', 'Database seeded')

    @staticmethod
    async def drop_tables() -> None:
        async with engine.begin() as conn:
            from app.core.db.base import BaseModel
            await conn.run_sync(BaseModel.metadata.drop_all)

    @staticmethod
    def create_service(model) -> None:
        return CRUDController(model)  # type: ignore

    @staticmethod
    def do_drop() -> None:
        from app import config
        config_yml = config.get_config_yml()
        if config_yml.app.environment.lower().startswith('prod'):
            cli_console.error(
                'Cannot reset the database in a production environment. Aborting.')
            raise typer.Abort()

        db_path = Path(config_yml.database.url_dirname())
        if not os.path.exists(db_path):
            cli_console.error(
                'Database does not exist. Cannot reset non-existent database.'
            )
            return
        asyncio.run(DBCommandUtils.drop_tables())


@db_app.command(help=CREATE_CMD_HELP)
def create() -> None:
    asyncio.run(connect_db())
    DBCommandUtils.seed_db()
    cli_console.info('Database created and seeded.')


@db_app.command(help=RESET_CMD_HELP)
def reset() -> None:
    from app import config
    DBCommandUtils.do_drop()

    yml = config.get_config_yml()

    if not yml.database.url.endswith(':memory:'):
        path = yml.database.url_dirname()

        if not os.path.exists(path):
            cli_console.error(
                'Database does not exist. Cannot reset non-existent database.'
            )
            typer.Abort()

        cli_console.info('Deleting database artifacts...')
        os.remove(path)

    asyncio.run(connect_db())
    DBCommandUtils.seed_db()
    cli_console.info('Database reset and seeded.')


@db_app.command(help='Drops the database tables.')
def drop() -> None:
    DBCommandUtils.do_drop()


@db_app.command(help=NAMES_CMD_HELP)
def names() -> None:
    model_map = get_model_map()
    for model in model_map.keys():
        cli_console.print_stdout(
            '[italic green]CLI Prefix:[/italic green]'
            f'[bold red]{model}\n[/bold red]'
            '[italic green]Model: [/italic green]'
            f'[bold red]{model_map[model].__name__}\n[/bold red]'
        )


@db_app.command(help=SHOW_CMD_HELP)
def show(
    model_name: str = typer.Argument(..., help='the model name to inspect')
) -> None:
    model_map = get_model_map()
    model_type = model_map.get(model_name)
    if not model_type:
        cli_console.error(
            f"UnknownModel: '{model_name}' not found in model map."
        )
        raise typer.Abort()

    orm_table = Table(
        title=f"Peek - {model_name}",
    )
    orm_columns = [column for column in model_type.__table__.columns]

    [orm_table.add_column(column.name) for column in orm_columns]

    service = DBCommandUtils.create_service(model_type)

    async def run_inspect() -> List[Any]:
        async with command_wrapper() as session:
            return await service.get_limited(session, 0, 10)  # type: ignore

    results = asyncio.run(run_inspect())
    for cols in results:
        orm_table.add_row(*[
            str(getattr(cols, column.name))
            for column in orm_columns
        ])

    cli_console.print_stdout(orm_table)


@db_app.command(help=TABLES_CMD_HELP)
def tables() -> None:
    table = Table(
        title='Database Tables',
        show_lines=True,
        style='cyan'
    )
    columns = ['Table Name', 'CLI Name', 'SQL Schema', 'Total Rows']
    [table.add_column(column) for column in columns]
    DBCommandUtils.get_model_data(table)
    cli_console.print_stdout(table)
