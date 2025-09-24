




from sqlalchemy.ext.asyncio import AsyncSession

from range_monitor.security import PasswordPolicy


async def insert_default_users(pwd_policy: PasswordPolicy, db: AsyncSession) -> None:
    from range_monitor.auth.repos.users import UserRepository
    from range_monitor.core.enums import UserRoles


    users = UserRepository(db)
    for role in UserRoles:
        if not await users.read.username_unique(role.value):
            continue

        pepper = pwd_policy.compute_pepper(role.value.encode('utf-8'))
        await users.write.create_user(
            username=role.value,
            password_hash=pwd_policy.bcrypt.hash(pepper),
            role=role,
        )

