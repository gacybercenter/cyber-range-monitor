import typer
import subprocess

app = typer.Typer()


@app.command(help='Builds the docker container')
def d_build(
    env: str = typer.Option(
        'dev',
        '--env',
        '-e', 
        help='The environment to build for'
    ),
) -> None:
    env_file = f'.{env}.env'
    typer.echo(f'Using env file: {env_file}')
    subprocess.run(
        ['docker', 'compose', '--env-file', env_file, 'build']
    )

@app.command()
def d_up(
    env: str = typer.Option(
        'dev',
        '--env',
        '-e',
        help='The environment to build for'
    )
) -> None:
    env_file = f'.{env}.env'
    typer.echo(f'Using env file: {env_file}')
    subprocess.run(
        ['docker', 'compose', '--env-file', env_file, 'up']
    )
    
def main() -> None:
    app()

if __name__ == '__main__':
    main()