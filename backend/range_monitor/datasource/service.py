
from contextlib import asynccontextmanager
from select import select
from typing import TYPE_CHECKING, Any, Generic, NamedTuple, TypeVar

from range_monitor.core.sql_repo import SqlRepo
from range_monitor.datasource.model import Guacamole, OpenStack, SaltStack
from range_monitor.errors import BadRequest, ResourceNotFound
from range_monitor.security import Encryptor

if TYPE_CHECKING:
    from range_monitor.datasource.specs import ConnectionSpec
    from range_monitor.params import PageParams
    from range_monitor.schema import PydanticMixin

class GuacamoleRepo(SqlRepo[Guacamole]):
    model = Guacamole


class OpenStackRepo(SqlRepo[OpenStack]):
    model = OpenStack


class SaltStackRepo(SqlRepo[SaltStack]):
    model = SaltStack




class DatasourceUtils:
    @staticmethod
    def add_password_ciphertext(params: dict, encryptor: Encryptor) -> None:
        if not (plaintext := params.pop('password', None)):
            return
        params['password_ciphertext'] = encryptor.encrypt(plaintext)

    @staticmethod
    def get_password_plaintext(ciphertext: str | None, encryptor: Encryptor) -> str | None:
        if not ciphertext:
            return None
        return encryptor.decrypt(ciphertext)

    @staticmethod
    @asynccontextmanager
    async def write_to_datasource(repo: SqlRepo):
        try:
            yield
        except Exception:
            await repo.db.rollback()
            raise BadRequest(f'Invalid paramaters for {repo.model.__name__}')

    @staticmethod
    async def create_datasource(
        params: PydanticMixin,
        repo: SqlRepo,
        encryptor: Encryptor
    ) -> Any:
        dict_params = params.dump()
        DatasourceUtils.add_password_ciphertext(dict_params, encryptor)

        async with DatasourceUtils.write_to_datasource(repo):
            new_datasource = repo.create(params=dict_params)
            await repo.save()

        return new_datasource

    @staticmethod
    async def update_datasource(
        datasource_id: str,
        params: PydanticMixin,
        repo: SqlRepo,
        encryptor: Encryptor
    ) -> Any:
        dict_params = params.model_dump(exclude_unset=True)
        if not dict_params:
            raise BadRequest('No parameters to update provided.')

        DatasourceUtils.add_password_ciphertext(dict_params, encryptor)

        if not (to_edit := await repo.get(datasource_id)):
            raise ResourceNotFound('DataSource')

        async with DatasourceUtils.write_to_datasource(repo):
            edit_datasource = await repo.update(to_edit, params=dict_params)

        return edit_datasource

    @staticmethod
    async def get_enabled_datasource(repo: SqlRepo) -> Any:
        statement = select(repo.model).where(repo.model.enabled.is_(True)) # type: ignore
        if not (datasource := await repo.first(statement)):
            raise ResourceNotFound('Enabled DataSource')
        return datasource



R = TypeVar('R', bound=SqlRepo)
S = TypeVar('S', bound=PydanticMixin)
C = TypeVar('C', bound=ConnectionSpec)

class DatasourcePage(NamedTuple, Generic[S]):
    total: int
    data: list[S]



class DataSourceService(Generic[R, S, C]):
    '''
    A generic service class for managing data sources,

    Overview
    --------
    This service class provides methods to create, update, and list data sources,
    as well as to create connection specifications based on existing data sources.

    When you inherit from this class, specify the following type parameters:
    Generics
    -------
    - R: The repository type, which should be a subclass of SqlRepo for the specific
    data source model.

    - S: The schema type, which should be a subclass of PydanticMixin representing
    the response schema for the data source.

    - C: The connection specification type, which should be a subclass of
    ConnectionSpec for creating connection specifications, i.e what are the parameters
    to create an API client or connection for the datasource.

    Class Variables
    ---------------
    - response_schema: The Pydantic schema class used for serializing data source,
    same as S.
    - spec: The ConnectionSpec class used for creating connection specifications,
    same as C.
    '''
    response_schema: type[S]
    spec: type[C]


    def __init__(
        self,
        repo: R,
        encryptor: Encryptor,
    ) -> None:
        self.repo: R = repo
        self.encryptor: Encryptor = encryptor

    async def create(self, params: PydanticMixin) -> S:
        new_datasource = await DatasourceUtils.create_datasource(
            params=params,
            repo=self.repo,
            encryptor=self.encryptor
        )
        return self.response_schema.convert(new_datasource)

    async def update(self, datasource_id: str, params: PydanticMixin) -> S:
        edit_datasource = await DatasourceUtils.update_datasource(
            datasource_id=datasource_id,
            params=params,
            repo=self.repo,
            encryptor=self.encryptor
        )
        return self.response_schema.convert(edit_datasource)

    async def list_datasources(self, page_params: PageParams) -> DatasourcePage[S]:
        statement = self.repo.select()
        total = await self.repo.get_query_total(statement)
        statement = page_params.paginate(statement)
        data: list[S] = []
        async for model in self.repo.stream(statement):
            data.append(self.response_schema.convert(model))
        return DatasourcePage(total=total, data=data)

    async def create_connection_spec(self, datasource_id: str | None = None) -> C:
        if datasource_id:
            datasource = await self.repo.get(datasource_id)
            if not datasource:
                raise ResourceNotFound('DataSource')
        else:
            datasource = await DatasourceUtils.get_enabled_datasource(self.repo)

        plaintext_password = DatasourceUtils.get_password_plaintext(
            ciphertext=datasource.password_ciphertext,
            encryptor=self.encryptor
        )
        if not plaintext_password:
            raise BadRequest('DataSource has no password set.')

        return self.spec.create_from_source(
            datasource=datasource,
            plaintext_password=plaintext_password
        )




