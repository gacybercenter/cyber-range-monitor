import typer

from scripts.prompts import CLIPrompts

from cli.config_utils import ConfigUtils


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

@config_app.command(help='creates the secrets')
def show(
    config_name: str = typer.Argument(
        default='APP_ENV',
        help='the configuration to show (e.g monitor config show -c APP_ENV)'
    )
) -> None:
    ConfigUtils.show_field_value(config_name)
    