import uuid
from typing import TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from range_monitor.errors import (
    DatasourceNotEnabled,
    ResourceNotFound,
)
from range_monitor.infra import sql_cmds
from range_monitor.infra.repos import SQLRepository
from range_monitor.infra.security._crypto import CryptoService
from range_monitor.sources.models import Datasource

D = TypeVar('D', bound=Datasource)


class DatasourceRepository(SQLRepository[D]):
    def __init__(
        self,
        db: AsyncSession,
        model: type[D],
        crypto: CryptoService,
    ) -> None:
        super().__init__(db, model=model)
        self.crypto_service = crypto

    async def is_label_unique(
        self, label: str, *, exclude_id: uuid.UUID | None = None
    ) -> bool:
        stmnt = select(self.model).where(self.model.label == label)
        if exclude_id:
            # type: ignore[attr-defined]
            stmnt = stmnt.where(self.model.id != exclude_id)

        return await self.first_row(stmnt) is None

    async def get_connected(self) -> D | None:
        stmnt = select(self.model).where(self.model.connected.is_(True))
        return await self.first_orm(stmnt)

    async def list_sources(
        self,
        label: str | None = None,
        *,
        converter=None,
        offset: int = 0,
        limit: int = 100,
    ) -> tuple[list[D], int]:
        assert callable(converter), 'converter must be a callable'
        stmnt = select(self.model).order_by(self.model.label.asc())

        if label:
            labels_ilike = sql_cmds.esc_like(f'%{label}%')
            expr = self.model.label.ilike(labels_ilike, escape='\\')
            stmnt = stmnt.where(expr)

        total = await self.count_rows(stmnt)

        models = []
        stmnt = stmnt.offset(offset).limit(limit)
        async for ds in self.stream_orms(stmnt):
            models.append(converter(ds))

        return models, total

    async def get_by_id(self, source_id: uuid.UUID) -> D | None:
        # type: ignore[arg-type]
        return await self.db.get(self.model, source_id)

    async def fetch(self, source_id: uuid.UUID) -> D:
        """
        Retrieves a datasource by its ID, if it does not exist,
        raises a 404.

        Parameters
        ----------
        source_id : uuid.UUID

        Returns
        -------
        D
            _description_

        Raises
        ------
        ResourceNotFound
            404
        """
        if not (source := await self.get_by_id(source_id)):
            raise ResourceNotFound('datasource')
        return source

    async def fetch_connected(self) -> D:
        if not (source := await self.get_connected()):
            raise DatasourceNotEnabled('datasource_not_enabled')
        return source

    def get_password(self, source: D) -> str:
        return self.crypto_service.decrypt_bytes(source.password_cipher)

    def encrypt_password(self, password: str) -> bytes:
        return self.crypto_service.encrypt_text(password)
