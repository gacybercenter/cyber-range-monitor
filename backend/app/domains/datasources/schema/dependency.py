

from enum import StrEnum
from typing import Self, Union

from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel

from sqlalchemy.ext.asyncio import AsyncSession

from ..guac.service import GuacamoleSourceService
from ..open_stack.service import OpenstackSourceService
from ..salt_stack.service import SaltstackSourceService


DatasourceService = Union[
    OpenstackSourceService,
    GuacamoleSourceService,
    SaltstackSourceService
]


class DatasourceType(StrEnum):
    OPEN_STACK = "openstack"
    GUAC = "guacamole"
    SALT_STACK = "saltstack"


class DatasourceMaster(BaseModel):
    '''wrapper object to simply have all of the services in a single instance
    for use in generalized routes in the datasource router.'''
    guacamole: GuacamoleSourceService
    openstack: OpenstackSourceService
    saltstack: SaltstackSourceService

    @classmethod
    def create(cls, db: AsyncSession) -> 'Self':
        return cls(
            guacamole=GuacamoleSourceService(db),
            openstack=OpenstackSourceService(db),
            saltstack=SaltstackSourceService(db)
        )


class ServiceContext(BaseModel):
    '''a wrapper object for the service dependency wrapper object
    to be used in the router to resolve the correct service.'''
    datasource: DatasourceType
    service: DatasourceService

    @classmethod
    def create_from_type(cls, datasource: DatasourceType, db: AsyncSession) -> 'Self':
        '''given a datasource type, it will resolve the type to correct service
        Arguments:
            datasource {Datasources} -- the type of the datasource
            db {AsyncSession} -- the database session for the service
        Raises:
            RequestValidationError: if the datasource is not recognized
            which will already be handled by FastAPI in the path parameter
        Returns:
            DatasourceContext -- class instance
        '''
        match datasource:
            case DatasourceType.OPEN_STACK:
                service = OpenstackSourceService(db)

            case DatasourceType.GUAC:
                service = GuacamoleSourceService(db)

            case DatasourceType.SALT_STACK:
                service = SaltstackSourceService(db)

            case _:
                raise RequestValidationError(
                    f'Unknown / Unrecognized datasource "{datasource}".'
                )

        return cls(service=service, datasource=datasource)
