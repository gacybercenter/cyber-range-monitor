import uuid
from collections.abc import Callable
from typing import Any, TypeVar

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from server.app import security
from server.db.repos import SQLRepository
from server.models.mixins import Datasource

D = TypeVar('D', bound=Datasource)


def _select_by_label[D: Datasource](
    model: type[D], *, label: str, exclude_id: uuid.UUID | None = None
) -> Select:
    stmnt = select(model).where(model.label == label)
    if exclude_id:
        stmnt = stmnt.where(model.id != exclude_id)
    return stmnt


class DatasourceRepository[D: Datasource](SQLRepository[D]):
    def __init__(
        self,
        model: type[D],
        *,
        db: AsyncSession,
    ) -> None:
        super().__init__(db=db, model=model)

    async def is_label_unique(
        self, label: str, *, exclude_id: uuid.UUID | None = None
    ) -> bool:
        stmnt = _select_by_label(
            self.model,
            label=label,
            exclude_id=exclude_id,
        )
        return await self.get_row(stmnt) is None

    async def get_connected(self) -> D | None:
        stmnt = select(self.model).where(self.model.connected.is_(True))
        return await self.get_model(stmnt)

    async def get_data_sources(
        self,
        *,
        converter: Callable[[dict], Any],
        offset: int = 0,
        limit: int = 100,
    ) -> tuple[list[D], int]:
        '''
        Retrieves a paginated list of datasources, optionally filtered by label.
        '''
        stmnt = select(self.model).order_by(self.model.label.asc())

        total = await self.count()

        stmnt = stmnt.offset(offset).limit(limit)
        models = [converter(ds) async for ds in self.stream_models(stmnt)]

        return models, total

    def get_password(self, source: D) -> str:
        return security.decrypt_ciphertext(source.password_cipher)

    def encrypt_password(self, password: str) -> bytes:
        return security.encrypt_plaintext(password)
