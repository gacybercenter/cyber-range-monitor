import typer
import asyncio


from api.db.main import get_session
from api.utils.cli.db_utils import CLIModelController, db_exists, initialize_database, reinit_database
from api.utils.cli.console import CLIConsole, DBConsole
from api.utils.cli.config_utils.configure import initialize_dev_settings


api_cli = typer.Typer()


@api_cli.command(help='Lists the table prefixes in the cli to pass into arguments')
def list_models() -> None:
    models_available = CLIModelController.list_model_names()
    DBConsole.model_name_panels(models_available)


@api_cli.command()
def show_tables(schemas: bool = typer.Option(False, '--schema', '-sc', help="Specifies whether to include the schemas for each of the tables.")) -> None:
    print(schemas)
    if not db_exists():
        CLIConsole.error(
            "Cannot show tables, database has not been initialized yet.")
        return

    async def display_table() -> None:
        await initialize_database(insert_defaults=False)
        async with get_session() as session:
            tables = await CLIModelController.get_table_metas(schemas, session)
            DBConsole.show_all_tables(schemas, tables)

    asyncio.run(display_table())


@api_cli.command(help="Inspect a table in the database. Usage 'inspect <model_name> [--schema]'")
def inspect(
    model_name: str = typer.Argument(
        ...,
        help="The name of the model to inspect."
    )
):
    async def run_inspect() -> None:
        await initialize_database(insert_defaults=False)
        async with get_session() as session:
            model_controller = CLIModelController.create_controller(model_name)
            table_info = await model_controller.table_info_meta(True, session)
            DBConsole.show_db_table(table_info)
    asyncio.run(run_inspect())


@api_cli.command(help="Initialize the database. Usage 'init-db [--no-seed | -ns]'\n Default is to seed the database with default data, flag to disable seeding.")
def init_db(
    seed: bool = typer.Option(
        True, '--no-seed', '-ns', help="Default is to seed the database with default data, flag to disable seeding."
    )
) -> None:
    async def run_init_db() -> None:
        await initialize_database(seed)
        CLIConsole.success("Database initialized successfully.")
    asyncio.run(run_init_db())


@api_cli.command(help='Re-initialize the database, deletes and then recreates it. Usage "reinit-db [--no-seed | -ns]"\n Default is to seed the database with default data, flag to disable seeding.')
def reinitialize_db(
    seed: bool = typer.Option(
        True, '--no-seed', '-ns', help="Default is to seed the database with default data, flag to disable seeding."
    )
) -> None:
    async def run_reinit_db() -> None:
        await reinit_database(seed)
        CLIConsole.success("Database re-initialized successfully.")
    asyncio.run(run_reinit_db())


@api_cli.command(help="Show the schema for a table in the database. Usage 'show-schema <table_name>'")
def show_schema(
    table_name: str = typer.Argument(
        ...,
        help="The name of the table to display the schema for."
    )
) -> None:
    async def run_show_schema() -> None:
        await initialize_database(insert_defaults=False)
        async with get_session() as session:
            model_controller = CLIModelController.create_controller(table_name)
            table_info = await model_controller.table_info_meta(True, session)
            DBConsole.show_db_table(table_info)
    asyncio.run(run_show_schema())


@api_cli.command(help='Select a record from a table in the database. Usage "select-id <model_name> <id>"')
def select_id(
    model: str = typer.Argument(
        ...,
        help="The name of the model to select from."
    ),
    id: int = typer.Argument(..., help="The id of the record to select.")
) -> None:
    async def run_select_id() -> None:
        await initialize_database(insert_defaults=False)
        async with get_session() as session:
            model_controller = CLIModelController.create_controller(model)
            result = await model_controller.get_id(id, session)
            CLIConsole.info(result)
    asyncio.run(run_select_id())


@api_cli.command(help='Read all records from a table in the database. Usage "read <model_name> [--limit | -l]"')
def read(
    model: str = typer.Argument(...,
                                help="The name of the model to select from."),
    limit: int = typer.Option(
        10, '--limit', '-l', help="The number of records to return.")
) -> None:
    async def run_read_all() -> None:
        await initialize_database(insert_defaults=False)
        async with get_session() as session:
            model_controller = CLIModelController.create_controller(model)
            results = await model_controller.read_all(limit, session)
            DBConsole.display_query_results(results)
    asyncio.run(run_read_all())


@api_cli.command(help='Initializes the development environment settings')
def init_env() -> None:
    CLIConsole.info('Initializing development environment settings...')
    initialize_dev_settings()


def main() -> None:
    try:
        api_cli()
    except Exception as e:
        CLIConsole.error(f"Error: {e}")


if __name__ == "__main__":
    main()
