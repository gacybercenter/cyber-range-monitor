import typer


def main() -> None:
    app = typer.Typer()
    from .config_app import config_app
    from .db_cli_app import db_app
    from .run_app import run_app

    app.add_typer(
        run_app,
        name='start',
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
    @app.command(help='export the openapi json')
    def export_openapi() -> None:
        import json

        from app.build import create_app
        with open('openapi.json', 'w') as f:
            f.write(json.dumps(create_app().openapi(), indent=2))
        print('openapi.json has been generated')
    app()


if __name__ == '__main__':
    main()
