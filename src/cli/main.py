import typer


def main() -> None:
    app = typer.Typer()
    from .api_run import run_app, docker_app
    from .api_config import config_app
    from .api_db import db_app

    app.add_typer(run_app, name='run', help='run the application')
    app.add_typer(docker_app, name='container',help='abbreviated docker commands')
    app.add_typer(config_app, name='config',
                  help='commands for the app config')
    app.add_typer(db_app, name='db', help='commands for the database')

    app()


if __name__ == '__main__':
    main()
