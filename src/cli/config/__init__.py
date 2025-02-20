import typer

from .utils import ConfigUtils


config_app = typer.Typer()


@config_app.command(help='Shows the documentation for the build settings')
def docs() -> None:
    ConfigUtils.show_help()


@config_app.command(help='Exits the application')
def env() -> None:
    ConfigUtils.show_env()


@config_app.command(help='Creates a template for the build settings')
def current_build() -> None:
    ConfigUtils.verbose_config()
