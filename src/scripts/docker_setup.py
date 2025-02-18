import os
import asyncio
from rich.console import Console


def main() -> None:
    console = Console()
    from scripts.dev_setup import create_env
    os.mkdir('instance')
    create_env(console, os.getenv('APP_ENV', 'prod'), True)

    import scripts.seed_db as seeder
    asyncio.run(seeder.run(console))
    
    

if __name__ == '__main__':
    main()
