import typer

from .utils.prompts import CLIPrompts
from .utils.config_utils import ConfigUtils


config_app = typer.Typer()


@config_app.command(help='shows the documentation for the configurations')
def docs() -> None:
    ConfigUtils.show_help()


@config_app.command(help='Shows the environment variables based on APP_ENV')
def env() -> None:
    ConfigUtils.show_env()


@config_app.command(help='Displays the verbose config')
def verbose() -> None:
    ConfigUtils.verbose_config()


@config_app.command(help='creates the secrets')
def create() -> None:
    from scripts.create_env import main
    CLIPrompts.info('Creating .env files...')
    main()
