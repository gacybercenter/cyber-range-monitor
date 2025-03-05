import asyncio
import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, AsyncGenerator, List

import typer
from rich.table import Table
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.schema import CreateTable

import app.db.seed as seed
from app.db.main import connect_db, engine, get_session
from app.shared.crud_mixin import CRUDService

from .prompts import CLIPrompts

db_app = typer.Typer()


@asynccontextmanager
async def command_wrapper() -> AsyncGenerator[AsyncSession, None]:
    await connect_db()
    async with get_session() as session:
        yield session


async def model_data(model_type: DeclarativeBase, prefix: str, session: AsyncSession) -> tuple:
    service = create_service(model_type)
    table_name = service.model.__tablename__
    sql_schema = str(CreateTable(model_type.__table__))  # type: ignore
    size = await service.size(session)

    return (table_name, prefix, sql_schema, size)


def get_model_data(table: Table) -> None:
    async def worker() -> None:
        from app.models import model_map
        async with command_wrapper() as session:
            for model in model_map:
                table_name, prefix, sql_schema, size = await model_data(model_map[model], model, session)
                table.add_row(table_name, prefix, sql_schema, str(size))
    asyncio.run(worker())


def seed_db() -> None:
    async def seeder() -> None:
        await seed.run()
    CLIPrompts.header('bold green', 'database_seeder')
    asyncio.run(seeder())
    CLIPrompts.header('bold blue', 'Database seeded')


async def drop_tables() -> None:
    app_env = os.getenv('APP_ENV', 'dev')
    if app_env.lower().startswith('prod'):
        CLIPrompts.error(
            'why u tyrna drop the db in prod'
        )
        raise typer.Abort()
    async with engine.begin() as conn:
        from app.models.base import Base
        await conn.run_sync(Base.metadata.drop_all)


def create_service(model: Any) -> Any:
    return CRUDService(model)  # type: ignore


@db_app.command(help='Creates the database and seeds the database')
def create() -> None:
    seed_db()
    CLIPrompts.info('Database and seed data initialized.')


@db_app.command(help='Reinitializes the database')
def reset() -> None:
    from app import config
    config_yml = config.get_config_yml()
    if config_yml.app.environment.lower().startswith('prod'):
        CLIPrompts.error(
            'Cannot reset the database in a production environment. Aborting.'
        )
        raise typer.Abort()
    
    CLIPrompts.print(
        '[bold red]WARNING[/bold red]'
        'Are you sure you want to proceed? This will delete all data in the database (Y/N).',
    )
    if not CLIPrompts.read().strip().lower()[0] == 'y':
        CLIPrompts.info('Aborting.')
        raise typer.Abort()

    db_path = Path(config_yml.database.resolve_url_dir())  # type: ignore
    if not os.path.exists(db_path):
        CLIPrompts.error(
            'Database does not exist. Cannot reset non-existent database.'
        )
        return
    asyncio.run(drop_tables())
    CLIPrompts.info('Database reinitialized.')
    seed_db()


@db_app.command(help='Shows the CLI names of the database tables')
def cli_names() -> None:
    from app.models import model_map
    for model in model_map.keys():
        CLIPrompts.print(
            '[italic green]CLI Prefix:[/italic green]'
            f'[bold red]{model}\n[/bold red]'
            '[italic green]Model: [/italic green]'
            f'[bold red]{model_map[model].__name__}\n[/bold red]'
        )


@db_app.command(help="Peeks a table in the database and shows 10 rows. Usage 'peek <model_name>'")
def peek(
    model_name: str = typer.Argument(..., help='the model name to inspect')
) -> None:
    from app.models import model_map
    model_type = model_map.get(model_name)
    if not model_type:
        CLIPrompts.error(
            f"UnknownModel: '{model_name}' not found in model map."
        )
        raise typer.Abort()

    orm_table = Table(
        title=f"Peek - {model_name}",
    )
    orm_columns = [column for column in model_type.__table__.columns]

    [orm_table.add_column(column.name) for column in orm_columns]

    service = create_service(model_type)

    async def run_inspect() -> List[Any]:
        async with command_wrapper() as session:
            return await service.get_limited(session, 0, 10)

    results = asyncio.run(run_inspect())
    for cols in results:
        orm_table.add_row(*[
            str(getattr(cols, column.name))
            for column in orm_columns
        ])

    CLIPrompts.print(orm_table)


@db_app.command(help="Shows the names of the tables in the database")
def tables() -> None:
    table = Table(
        title='Database Tables',
        show_lines=True,
        style='cyan',
    )
    columns = ['Table Name', 'Model Map Prefix', 'SQL Schema', 'Total Rows']
    [table.add_column(column) for column in columns]
    get_model_data(table)
    CLIPrompts.print(table)
