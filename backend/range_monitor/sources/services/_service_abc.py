import uuid
from typing import TYPE_CHECKING, Generic, TypeVar

from sqlalchemy.ext.asyncio import AsyncSession

from range_monitor.errors import (
    BadRequest,
    ConflictError,
    DatasourceNotEnabled,
    ResourceNotFound,
)
from range_monitor.infra.security import CryptoService
from range_monitor.sources._adapter_abc import APISourceAdapter
from range_monitor.sources.repo import D, DatasourceRepository

if TYPE_CHECKING:
    from range_monitor.core.schema import PydanticMixin


C = TypeVar('C')


class DatasourceService(Generic[D, C]):
    model: type[D]

    def __init__(
        self,
        db: AsyncSession,
        *,
        crypto_service: CryptoService,
        api_adapter: APISourceAdapter[D, C],
    ) -> None:
        self.sources: DatasourceRepository[D] = DatasourceRepository(
            db,
            model=self.model,
            crypto=crypto_service,
        )
        self.api_adapter: APISourceAdapter = api_adapter

    async def create_source(self, body: 'PydanticMixin') -> D:
        """
        Creates a new datasource, using the request body schema.

        Parameters
        ----------
        body : PydanticMixin

        Returns
        -------
        D

        Raises
        ------
        BadRequest
            The request body is missing required fields.
        ConflictError
            The label provided is already in use.
        """
        params = body.dump()

        if not (password := params.pop('password')):
            raise BadRequest('fields_missing')

        if not await self.sources.is_label_unique(params['label']):
            raise ConflictError('label_taken')

        params['password_cipher'] = self.sources.encrypt_password(password)

        return await self.sources.create(**params)

    async def patch_source(self, source_id: uuid.UUID, body: 'PydanticMixin') -> D:
        """
        Updates an existing datasource, using the request body schema.

        Parameters
        ----------
        source_id : uuid.UUID
        body : PydanticMixin

        Returns
        -------
        D

        Raises
        ------
        ResourceNotFound
            The datasource with the provided ID does not exist.
        BadRequest
            The request body is missing required fields.
        ConflictError
            The label provided is already in use.
        """
        target = await self.sources.fetch(source_id)

        params = body.dump()

        if password := params.pop('password', None):
            params['password_cipher'] = self.sources.encrypt_password(password)

        if 'label' in params and not await self.sources.is_label_unique(
            params['label'], exclude_id=source_id
        ):
            raise ConflictError('label_taken')

        await self.sources.update(target, **params)
        return target

    async def connect_to(self, source: D) -> C:
        """
        Connects to a given datasource, assumes that the datasource
        has `connected` set to true or will be set by the caller.

        Parameters
        ----------
        source : D

        Returns
        -------
        C

        Raises
        ------
        ConflictError
        """
        password = self.sources.get_password(source)
        test_results = await self.api_adapter.test_connection(source, password)
        if not test_results.success:
            err = test_results.error or 'error_not_specified'
            raise ConflictError(f'Could not connect to datasource, {err}')

        if await self.api_adapter.get_connection():
            await self.api_adapter.close_connection()

        return await self.api_adapter.connect(source, password)

    async def connect_by_id(self, source_id: uuid.UUID) -> D:
        """
        Connects to a source by its ID, if the source was already
        enabled, it raises a ConflictError. If the datasource does not exist,
        it raises a ResourceNotFound error.

        - If there was a previously enabled datasource, it will be disabled
        and the connection closes.

        - The newly selected datasource will be marked as enabled, meaning
        next time `get_connection` is called, it will connect to the datasource.

        Parameters
        ----------
        source_id : uuid.UUID

        Returns
        -------
        D

        Raises
        ------
        ConflictError
        ResourceNotFound
        """

        target = await self.sources.fetch(source_id)

        if old := await self.sources.get_connected():
            if old.id == target.id:
                raise ConflictError('already_connected')

            old.connected = False

        await self.connect_to(target)
        target.connected = True
        await self.sources.save()

        return target

    async def delete_source(self, source_id: uuid.UUID) -> None:
        """
        Deletes a datasource by its ID, if the datasource was
        enabled, it also invalidates removes it's ID and closes any active
        connections.

        Parameters
        ----------
        source_id : uuid.UUID

        Raises
        ------
        ResourceNotFound
        """
        if not (ds := await self.sources.get_by_id(source_id)):
            raise ResourceNotFound('datasource')

        was_connected = ds.connected
        await self.sources.delete(ds)
        if was_connected:
            await self.api_adapter.close_connection()

        await self.sources.delete(ds)

    async def get_connection(self) -> C:
        """
        Retrieves the current connection if it exists, otherwise
        it attempts to connect to the currently enabled datasource.
        If no datasource is currently enabled, it raises a DatasourceNotEnabled error.

        Returns
        -------
        C

        Raises
        ------
        DatasourceNotEnabled
        """
        if conn := await self.api_adapter.get_connection():
            return conn

        if not (source := await self.sources.get_connected()):
            raise DatasourceNotEnabled()

        return await self.connect_to(source)

    async def test_connection(self, source_id: uuid.UUID) -> dict:
        target = await self.sources.fetch(source_id)

        password = self.sources.get_password(target)
        result = await self.api_adapter.test_connection(target, password)
        return {'success': result.success, 'error': result.error}

    async def disconnect(self) -> None:
        """
        Disables any currently enabled datasource, if one exists.

        Raises
        ------
        ResourceNotFound
            No datasource is currently enabled.
        """
        old = await self.sources.fetch_connected()

        old.connected = False  # type: ignore
        await self.sources.save()
        await self.api_adapter.close_connection()

    async def read_by_id(self, source_id: uuid.UUID) -> D:
        """
        Fetches a datasource by its ID.

        Parameters
        ----------
        source_id : uuid.UUID

        Returns
        -------
        D

        Raises
        ------
        ResourceNotFound
            The datasource with the provided ID does not exist.
        """
        return await self.sources.fetch(source_id)

    async def read_connected(self) -> D:
        """
        Fetches the currently enabled datasource.

        Returns
        -------
        D

        Raises
        ------
        ResourceNotFound
            No datasource is currently enabled.
        """
        return await self.sources.fetch_connected()
