




from sqlalchemy.ext.asyncio import AsyncSession

from range_monitor.security import PasswordHashes


async def seed_default_users(pwd_hasher: 'PasswordHashes', db: AsyncSession) -> None:
    from range_monitor.users.repo import UserRepo
    from range_monitor.users.roles import UserRoles


    users = UserRepo(db)
    for role in UserRoles:
        if not await users.is_username_unique(role.value):
            continue

        users.create(
            username=role.value,
            password_hash=pwd_hasher.hash_password(role),
            role=role.value,
        )

