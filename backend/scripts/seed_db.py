import asyncio

from rich.console import Console
from app.security import crypto_utils
from app.db import get_session, connect_db
from app.models.enums import LogLevel
from app.models import (
    Guacamole,
    Openstack,
    Saltstack,
    EventLog,
    User,
    Role
)
from ..cli.prompts import CLIPrompts


async def insert_seed_data() -> None:
    async with get_session() as db:
        for labels in SEED_DATA.keys():
            print('Inserting seed data for', labels)
            for seeds in SEED_DATA[labels]:
                db.add(seeds)
        await db.commit()


async def run() -> None:
    CLIPrompts.header('bold green', 'seed_db.py')
    await connect_db()
    await insert_seed_data()
