from typing import Any, List
import typer
import asyncio

from pathlib import Path
from app.db import connect_db, get_session
from app.common.crud_mixin import CRUDService, ModelT
from app.models import model_map
from rich.console import Console
from rich import table
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.schema import CreateTable
from sqlalchemy.ext.asyncio import AsyncSession

api_cli = typer.Typer()

console = Console()


def create_service(model: ModelT) -> CRUDService[ModelT]:
    return CRUDService(model)  # type: ignore


async def model_info(model_type: DeclarativeBase, prefix: str, session: AsyncSession) -> tuple:
    service = create_service(model_type)
    table_name = service.model.__tablename__
    sql_schema = str(CreateTable(model_type.__table__))  # type: ignore
    size = await service.total_records(session)

    return (table_name, prefix, sql_schema, size)


@api_cli.command(help='Shows the database tables and their information. Usage: "show_tables"')
def show_tables() -> None:
    model_table = table.Table(
        title="Database Models",
        show_header=True,
        style='cyan'
    )

    columns = ['Table Name', 'Model Map Prefix', 'SQL Schema', 'Total Rows']
    [model_table.add_column(column) for column in columns]

    async def create_table_view() -> None:
        await connect_db()
        async with get_session() as session:
            for model in model_map:
                table_name, prefix, sql_schema, size = await model_info(model_map[model], model, session)
                model_table.add_row(table_name, prefix, sql_schema, str(size))

    asyncio.run(create_table_view())

    console.print(model_table)


@api_cli.command(help="Inspect a table in the database. Usage 'inspect <model_name>'")
def inspect(
    model_name: str = typer.Argument(
        ...,
        help="The name of the model to inspect."
    )
) -> None:
    model_type = model_map.get(model_name)
    if not model_type:
        raise typer.BadParameter(
            f"Model '{model_name}' not found in model map.")

    orm_table = table.Table(
        title=f"Preview {model_name}",
    )
    orm_columns = [column for column in model_type.__table__.columns]

    [orm_table.add_column(column.name) for column in orm_columns]

    service = create_service(model_type)

    async def run_inspect() -> List[Any]:
        await connect_db()
        async with get_session() as session:
            return await service.get_limited(session, 0, 10)

    results = asyncio.run(run_inspect())
    for cols in results:
        orm_table.add_row(*[str(getattr(cols, column.name))
                          for column in orm_columns])

    console.print(orm_table)


@api_cli.command(help='creates the database')
def create_db() -> None:
    async def run_create_db() -> None:
        from scripts.seed_db import main
        await main()
    asyncio.run(run_create_db())
    console.print('[green]Database created.[/green]')


@api_cli.command(help='reinitilaizes the database')
def reinit_db() -> None:
    proceed = input(
        'This will drop all of the tables is this ok (type YES to continue): '
    ).lower().strip()

    if proceed != 'yes':
        console.print('[red]Aborting...[/red]')
        return

    db_path = Path('instance', 'app.db')
    if not db_path.exists():
        console.print('[red]Database does not exist.[/red]')
        return

    db_path.unlink()

    async def run_reinit_db() -> None:
        from scripts.seed_db import main
        await main()

    asyncio.run(run_reinit_db())


@api_cli.command(help='drops the database')
def model_names() -> None:
    for model in model_map.keys():
        console.print(
            '[italic green]Prefix:[/italic green]'
            f'[bold red]{model}\n[/bold red]'
            '[italic green]Model: [/italic green]'
            f'[bold red]{model_map[model].__name__}\n[/bold red]'
        )


@api_cli.command(help='copies the environment variables to clipboard to paste in .env file')
def env_vars() -> None:
    choice = input(
        '? Create the .env file? (type YES if so): ').lower().strip()
    if choice == 'yes':
        with open('.env', 'w') as f:
            pass
        console.print('[green].env file created.[/green]')

    from scripts.key_gen import main
    console.print(
        '[green]Running scripts\\key_gen.py.[/green]'
    )
    main()


def cli_main() -> None:
    try:
        api_cli()
    except Exception as e:
        console.print(
            f'[red]Unhandled CLI error: [/red] {e}'
        )


if __name__ == "__main__":
    cli_main()
