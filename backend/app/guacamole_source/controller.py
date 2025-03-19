
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

import guacamole

from app.extensions.datasources.controller import DatasourceController

from app.extensions.datasources.errors import NoEnabledDatasourceError

from .model import GuacamoleSource
from .schema import (
    GuacamoleListResponse,
    GuacamoleProtectedRead,
    GuacamoleSessionConfig
)


class GuacamoleController(DatasourceController):
    '''The controller for the Guacamole datasource'''

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(GuacamoleSource, db)

    async def connect_args(self, guac_source: GuacamoleSource) -> GuacamoleSessionConfig:
        '''returns the connection arguments for the Guacamole datasource
        Arguments:
            guac_source {GuacamoleSource} -- the Guacamole datasource
        Returns:
            dict -- the connection arguments
        '''
        password = await self.read_datasource_password(guac_source)
        return GuacamoleSessionConfig(
            host=guac_source.endpoint,
            username=guac_source.username,
            password=password,
            data_source=guac_source.datasource
        )
    
    
    async def test_connection(self, id: int) -> bool:
        '''tests the connection to the Guacamole datasource by it's ID

        Arguments:
            id {int} -- the ID of the datasource to connect to

        Returns:
            bool -- whether the connection was successful
        '''
        guac_session = await self.connect_by_id(id)
        return guac_session is not None

    async def connect_by_id(self, source_id: int) -> Optional[guacamole.session]:
        '''given a Guacamole datasource ID, creates a guacamole session and returns the session object
        Arguments:
            source_id {int} -- the ID of the Guacamole datasource to connect to
        Returns:
            Optional[guacamole.session] -- the guacamole session object if the connection was successful, None otherwise
        '''
        source = await self.get_by_id(source_id)
        session_config = await self.connect_args(source)
        return await self.connect(session_config)
        

    async def connect_enabled(self) -> Optional[guacamole.session]:
        '''creates a guacamole session from the enabled Guacamole datasource and returns the session object
        Returns:
            Optional[guacamole.session] -- the guacamole session object if the connection was successful, None otherwise
        '''
        enabled_source: GuacamoleSource = await self.get_enabled_source() 
        if not enabled_source:
            raise NoEnabledDatasourceError('No enabled Guacamole datasource found')
        session_config = await self.connect_args(enabled_source)
        return await self.connect(session_config)    
    
    
    async def connect(self, session_config: GuacamoleSessionConfig) -> Optional[guacamole.session]:
        '''creates a guacamole session from the Guacamole datasource and returns the session object
        Arguments:
            guac_source {GuacamoleSource} -- the Guacamole datasource to connect to
        Returns:
            Optional[guacamole.session] -- the guacamole session object or None if the 
            connection failed & a key error occured
        '''
        try:
            args = session_config.model_dump()
            return guacamole.session(**args)
        except Exception:
            return None

    async def protected_read(self, id: int) -> GuacamoleProtectedRead:
        '''returns a Guacamole datasource with protected fields
        Arguments:
            id {int} -- the ID of the datasource to read
        Returns:
            GuacamoleRead -- the Guacamole datasource with protected fields
        '''
        guac_source, password = await super().protected_read(id)
        protected_schema = GuacamoleProtectedRead.to_model(guac_source)
        protected_schema.password = password
        return protected_schema

    async def get_all_sources(self) -> GuacamoleListResponse:
        '''returns all the Guacamole datasources
        Returns:
            GuacamoleListResponse -- the list of all Guacamole datasources
        '''
        guac_sources: list[GuacamoleSource] = await super().get_all_sources()
        list_response = GuacamoleListResponse.from_list(guac_sources)
        return list_response
    
    
    

    
    