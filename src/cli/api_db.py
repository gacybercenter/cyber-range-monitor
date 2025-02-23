import asyncio
from pathlib import Path
import typer
from typing import Any, AsyncGenerator, List
from contextlib import asynccontextmanager
from rich.table import Table

from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.schema import CreateTable
from sqlalchemy.ext.asyncio import AsyncSession
from app.utils.crud_mixin import CRUDService, ModelT

from app.models import model_map
from app.db import get_session, connect_db
from scripts.prompts import CLIPrompts


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
    size = await service.total_records(session)

    return (table_name, prefix, sql_schema, size)


def get_model_data(table: Table) -> None:
    async def worker() -> None:
        async with command_wrapper() as session:
            for model in model_map:
                table_name, prefix, sql_schema, size = await model_data(model_map[model], model, session)
                table.add_row(table_name, prefix, sql_schema, str(size))
    asyncio.run(worker())


def seed_db() -> None:
    async def seed() -> None:
        import cli.scripts.seed_db as seeder
        await seeder.run()
    CLIPrompts.header('bold green', 'seed_db.py')
    asyncio.run(seed())


def create_service(model: ModelT) -> CRUDService[ModelT]:
    return CRUDService(model)  # type: ignore


@db_app.command(help='Creates the database and seeds the database')
def create() -> None:
    seed_db()
    CLIPrompts.info('Database and seed data initialized.')


@db_app.command(help='Reinitializes the database')
def reset() -> None:
    CLIPrompts.print(
        '[bold red]WARNING[/bold red]'
        'Are you sure you want to proceed? This will delete all data in the database (Y/N).',
    )
    if not CLIPrompts.read().strip().lower() != 'y':
        CLIPrompts.info('Aborting.')
        raise typer.Abort()

    db_path = Path('instance', 'app.db')
    if not db_path.exists():
        CLIPrompts.error(
            'Database does not exist. Cannot reset non-existent database.'
        )
        return

    db_path.unlink()
    seed_db()
    CLIPrompts.info('Database reinitialized.')


@db_app.command(help='Shows the CLI names of the database tables')
def cli_names() -> None:
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
