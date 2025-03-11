import typer


def main() -> None:
    app = typer.Typer()
    from .cli_config_api import config_app
    from .db_cli_app import db_app
    from .cli_start_api import run_app

    app.add_typer(
        run_app,
        name='start',
        help='run the application'
    )
    app.add_typer(
        config_app,
        name='conf',
        help='commands for the app config'
    )
    app.add_typer(
        db_app,
        name='db',
        help='commands for the database'
    )
    app()


if __name__ == '__main__':
    main()
