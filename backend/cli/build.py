import typer
from typing import Optional


def main() -> None:
    app = typer.Typer(
        help='Main application with multiple commands, type --help <sub_group> for more information about each'
    )

    from .cli_config_api import config_app
    from .cli_start_api import run_app

    nampespaces = [
        ('start', run_app, 'Run the application with specified configuration'),
        ('conf', config_app, 'Manage application configuration settings'),
    ]

    for name, sub_app, help in nampespaces:
        app.add_typer(sub_app, name=name, help=help)

    app()


if __name__ == '__main__':
    main()
