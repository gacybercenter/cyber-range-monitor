

import abc
from typing import TYPE_CHECKING, Generic, NamedTuple, TypeVar

from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession

from range_monitor.core.sql_repo import SqlRepo
from range_monitor.datasource.connection_abc import DatasourceConnection
from range_monitor.datasource.model import Datasource
from range_monitor.errors import BadRequest, ResourceNotFound
from range_monitor.schema import PydanticMixin
from range_monitor.security import Encryptor

if TYPE_CHECKING:
    from range_monitor.params import PageParams, TimestampParams


D = TypeVar('D', bound=Datasource)
S = TypeVar('S', bound='PydanticMixin')


class DatasourceCredentials(NamedTuple, Generic[D]):
    adapter: D
    password: str

class DatasourcePage(NamedTuple, Generic[S]):
    total: int
    items: list[S]



class DatasourceService(Generic[D], abc.ABC):
    '''
    Abstract base class for the shared logic across each
    of the individual Datasources supported by the range
    monitor. Including CRUD operations, enabling/disabling,
    pagination and resolving the ORM into a client factory.

    Class Attributes
    ----------------
    datasouce_orm : type[Datasource]
        _The ORM model class for the datasource type,
        you must set this in subclasses._
    connector : type[DatasourceConnector]
        _The connector class which resolves the ORM into
        a client, you must set this in subclasses._

    Abstract Methods
    ----------------
    test_connection
        _Tests a datasource to see if it's connection can be resolved,
        should not raise_
    connect
        _Creates and returns a client instance, should raise
        an error if it fails_

    '''
    datasouce_orm: type[D]
    connection: DatasourceConnection


    def __init__(
        self,
        *,
        db: AsyncSession,
        encryptor: Encryptor,
    ) -> None:
        self.repo: SqlRepo[D] = SqlRepo(db, model=self.datasouce_orm)
        self.encryptor: Encryptor = encryptor


    async def get_datasource(self, adapter_id: str) -> D:
        '''
        Get adapter by ID, raises 404 if not found.

        Parameters
        ----------
        adapter_id : str

        Returns
        -------
        A

        Raises
        ------
        ResourceNotFound
        '''
        if not (adapter := await self.repo.get(adapter_id)):
            raise ResourceNotFound('Adapter not found.')
        return adapter


    def query_datasources(self, timestamps: 'TimestampParams') -> Select:
        '''
        Builds a query for adapters applying timestamp filters.

        Parameters
        ----------
        timestamps : TimestampParams

        Returns
        -------
        Select
        '''
        query = timestamps.apply(
            self.repo.select(),
            self.datasouce_orm.created_at,
            self.datasouce_orm.updated_at,
        )

        return query.order_by(
            self.datasouce_orm.username,
            self.datasouce_orm.created_at,
        )


    async def paginate_datasources(
        self,
        page: 'PageParams',
        timestamps: 'TimestampParams',
        *,
        dto: type[S]
    ) -> DatasourcePage[S]:
        '''
        Accepts a page and timestamp params and dto or (data transfer object)
        to convert the ORM into, returns a named tuple containing the total
        number of items returned (ignoring pagination) and a list

        Parameters
        ----------
        page : PageParams
        timestamps : TimestampParams
        dto : type[S]

        Returns
        -------
        DatasourcePage[S]
        '''
        query = self.query_datasources(timestamps)

        total = await self.repo.get_query_total(query)
        paginated_query = page.paginate(query)

        dtos = []
        async for adapter in self.repo.stream(paginated_query):
            dtos.append(
                dto.convert(adapter)
            )

        return DatasourcePage[S](
            total=total,
            items=dtos
        )


    async def enable_by_id(self, datasource_id: str) -> D:
        '''
        Enables the adapter with the given ID, disabling any previously
        enabled

        Parameters
        ----------
        adapter_id : str

        Returns
        -------
        A

        Raises
        ------
        BadRequest
            _The adapter ID is already enabled_
        '''
        to_enable = await self.get_datasource(datasource_id)

        if to_enable.enabled:
            raise BadRequest('Adapter is already enabled.')

        await self.repo.batch_update(
            {'enabled': False},
            self.repo.model.enabled.is_(True)
        )

        to_enable.enabled = True
        await self.repo.save(to_enable)

        return to_enable

    async def disable(self) -> None:
        '''
        Disables any currently enabled adapter.
        '''
        await self.repo.batch_update(
            {'enabled': False},
            self.repo.model.enabled.is_(True)
        )
        await self.repo.save()

    async def create_datasource(self, create_body: PydanticMixin) -> D:
        '''
        Creates a new adapter from the given body.

        Parameters
        ----------
        create_body : PydanticMixin
            _The parameters to create the adapter_

        Returns
        -------
        A
            _The new model_
        '''
        params = create_body.dump(by_alias=False)
        if not (plaintext_pwd := params.pop('password')):
            raise BadRequest('A password is required to create a datasource.')

        params['password_ciphertext'] = self.encryptor.encrypt(
            plaintext_pwd
        )

        adapter = self.repo.create(**params)
        await self.repo.save()
        return adapter


    async def update_datasource_id(
        self,
        datasource_id: str,
        update_body: PydanticMixin
    ) -> D:
        '''
        Updates an existing datasource with the given body.

        Parameters
        ----------
        adapter_id : str
            _The ID of the adapter to update_
        update_body : PydanticMixin
            _The parameters to update the adapter_

        Returns
        -------
        A

        Raises
        ------
        BadRequest
            _The update failed_
        '''
        adapter = await self.get_datasource(datasource_id)

        params = update_body.dump(by_alias=False)

        if password := params.pop('password', None):
            params['password_ciphertext'] = self.encryptor.encrypt(password)

        updated_adapter = await self.repo.update(adapter, params)
        if not updated_adapter:
            raise BadRequest('Invalid configuration for adapter.')

        return updated_adapter


    async def delete_datasource_id(self, datasource_id: str) -> None:
        '''
        Deletes the datasource with the given ID.

        Raises
        ------
        ResourceNotFound
            _The adapter was not found_

        Parameters
        ----------
        datasource_id : str
            _The datasource id_
        '''
        adapter = await self.get_datasource(datasource_id)
        await self.repo.delete(adapter)


    async def get_enabled_datasource(self) -> D | None:
        statement = self.repo.select().where(
            self.repo.model.enabled.is_(True)
        )
        return await self.repo.first(statement)

    async def grab_enabled_datasource(self) -> D:
        '''
        Fetches the currently enabled adapter,
        raises 404 if none found.

        Returns
        -------
        D
            _The enabled datasource_

        Raises
        ------
        ResourceNotFound
            _No datasource is enabled_
        '''
        enabled_datasource = await self.get_enabled_datasource()

        if not enabled_datasource:
            raise BadRequest('No datasource is enabled.')

        return enabled_datasource

    async def get_credentials(
        self,
        datasource_id: str | None = None
    ) -> DatasourceCredentials[D]:
        '''
        Gets either the enabled datasource (if no ID is given)
        or the datasource with the given ID, decrypts the password
        and returns both in a named tuple to be passed to the
        adapter methods.

        Parameters
        ----------
        datasource_id : str | None, optional
            _Optional ID to get for the datasource_, by default None

        Returns
        -------
        DatasourceCredentials[D]
            _The named tuple with the plain password and datasource model_
        '''
        if not datasource_id:
            datasource = await self.grab_enabled_datasource()
        else:
            datasource = await self.get_datasource(datasource_id)

        plaintext_pwd = self.encryptor.decrypt(
            datasource.password_ciphertext
        )

        return DatasourceCredentials[D](
            adapter=datasource,
            password=plaintext_pwd
        )