import typer


def main() -> None:
    app = typer.Typer()
    from .run_app import run_app
    from .config_app import config_app
    from .db_cli_app import db_app

    app.add_typer(
        run_app,
        name='run',
        help='run the application'
    )
    app.add_typer(
        config_app,
        name='config',
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
