import typer

app = typer.Typer()


def resgiter_namespaces(namespace: typer.Typer) -> None:
    from .api_db import db_app
    from .config import config_app
    app.add_typer(db_app, name='db', help='interact with the database')
    app.add_typer(config_app, name='config', help='interact with the build config')
    
    
    