import uuid
from typing import TYPE_CHECKING, Any

from sqlalchemy.ext.asyncio import AsyncSession

from server.app.data_sources.repo import DatasourceRepository
from server.app.errors.http import (
    BadRequestError,
    ConflictError,
    DatasourceNotEnabledError,
    NotFoundError,
)
from server.external.adapters import DatasourceAdapter
from server.models.mixins import Datasource

if TYPE_CHECKING:
    from server.schema import PydanticModel


class DatasourceService[D: Datasource, C: Any]:
    model: type[D]

    def __init__(
        self,
        db: AsyncSession,
        *,
        adapter: DatasourceAdapter[D, C],
    ) -> None:
        self.sources: DatasourceRepository[D] = DatasourceRepository(
            db=db,
            model=self.model,
        )
        self.adapter: DatasourceAdapter = adapter

    async def get_by_id(self, source_id: uuid.UUID) -> D:
        '''
        Retrieves a datasource by its ID, if it does not exist,
        raises a 404.

        Parameters
        ----------
        source_id : uuid.UUID
            The unique identifier of the datasource.

        Returns
        -------
        D

        Raises
        ------
        NotFoundError
            404
        '''
        if not (source := await self.sources.read(source_id)):
            raise NotFoundError('datasource')

        return source

    async def get_connected_source(self) -> D:
        if not (source := await self.sources.get_connected()):
            raise DatasourceNotEnabledError('datasource_not_enabled')
        return source

    async def create_data_source(self, body: 'PydanticModel') -> D:
        '''
        Creates a new datasource, using the request body schema.

        Parameters
        ----------
        body : PydanticModel
            The body to create the datasource from.

        Returns
        -------
        D

        Raises
        ------
        BadRequestError
            The request body is missing required fields.
        ConflictError
            The label provided is already in use.
        '''
        params = body.dump()

        if not (password := params.pop('password')):
            raise BadRequestError('fields_missing')

        if not await self.sources.is_label_unique(params['label']):
            raise ConflictError('label_taken')

        params['password_cipher'] = self.sources.encrypt_password(password)

        return await self.sources.insert(**params)

    async def update_data_source(self, source_id: uuid.UUID, body: 'PydanticModel') -> D:
        '''
        Updates an existing datasource, using the request body schema.

        Parameters
        ----------
        source_id : uuid.UUID
            The ID of the datasource to update.
        body : PydanticModel
            The body to update the datasource from.

        Returns
        -------
        D

        Raises
        ------
        NotFoundError
            The datasource with the provided ID does not exist.
        BadRequestError
            The request body is missing required fields.
        ConflictError
            The label provided is already in use.
        '''
        target = await self.get_by_id(source_id)

        params = body.dump()

        if password := params.pop('password', None):
            params['password_cipher'] = self.sources.encrypt_password(password)

        if 'label' in params and not await self.sources.is_label_unique(
            params['label'],
            exclude_id=source_id
        ):
            raise ConflictError('label_taken')

        await self.sources.update(target, **params)
        return target

    async def connect_data_source(self, source: D) -> C:
        '''
        Connects to a given datasource, assumes that the datasource
        has `connected` set to true or will be set by the caller.

        Parameters
        ----------
        source : D
            The datasource to connect to.

        Returns
        -------
        C

        Raises
        ------
        ConflictError
        '''
        password = self.sources.get_password(source)
        test_results = await self.adapter.test_connection(source, password)
        if not test_results.success:
            err = test_results.error or 'error_not_specified'
            raise ConflictError(f'Could not connect to datasource, {err}')

        if await self.adapter.get_connection():
            await self.adapter.close_connection()

        return await self.adapter.connect(source, password)

    async def connect_by_id(self, source_id: uuid.UUID) -> D:
        '''
        Connects to a source by its ID, if the source was already
        enabled, it raises a ConflictError. If the datasource does not exist,
        it raises a NotFoundError error.

        - If there was a previously enabled datasource, it will be disabled
        and the connection closes.

        - The newly selected datasource will be marked as enabled, meaning
        next time `get_connection` is called, it will connect to the datasource.

        Parameters
        ----------
        source_id : uuid.UUID
            The ID of the datasource to connect to.

        Returns
        -------
        D

        Raises
        ------
        ConflictError
        NotFoundError
        '''

        target = await self.get_by_id(source_id)

        if old := await self.sources.get_connected():
            if old.id == target.id:
                raise ConflictError('already_connected')
            old.connected = False

        await self.connect_data_source(target)
        target.connected = True
        await self.sources.save()

        return target

    async def delete_data_source(self, source_id: uuid.UUID) -> None:
        '''
        Deletes a datasource by its ID, if the datasource was
        enabled, it also invalidates removes it's ID and closes any active
        connections.

        Parameters
        ----------
        source_id : uuid.UUID
            The ID of the datasource to delete

        Raises
        ------
        NotFoundError
        '''
        ds = await self.get_by_id(source_id)

        was_connected = ds.connected
        await self.sources.delete(ds)
        if was_connected:
            await self.adapter.close_connection()

        await self.sources.delete(ds)

    async def get_connection(self) -> C:
        '''
        Retrieves the current connection if it exists, otherwise
        it attempts to connect to the currently enabled datasource.
        If no datasource is currently enabled, it raises a DatasourceNotEnabledError
        error.

        Returns
        -------
        C

        Raises
        ------
        DatasourceNotEnabledError
        '''
        if conn := await self.adapter.get_connection():
            return conn

        if not (source := await self.sources.get_connected()):
            raise DatasourceNotEnabledError

        return await self.connect_data_source(source)

    async def test_connection(self, source_id: uuid.UUID) -> dict:
        target = await self.get_by_id(source_id)

        password = self.sources.get_password(target)
        result = await self.adapter.test_connection(target, password)
        return {'success': result.success, 'error': result.error}

    async def disconnect_data_source(self) -> None:
        '''
        Disables any currently enabled datasource, if one exists.

        Raises
        ------
        NotFoundError
            No datasource is currently enabled.
        '''
        old = await self.get_connected_source()
        old.connected = False  # type: ignore
        await self.sources.save()
        await self.adapter.close_connection()
