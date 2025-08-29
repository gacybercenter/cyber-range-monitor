

from sqlalchemy.ext.asyncio import AsyncSession

from .repo import SaltStackRepo


class SaltStackAdapter:

    def __init__(self, session: AsyncSession) -> None:
        self.repo: SaltStackRepo = SaltStackRepo(session)