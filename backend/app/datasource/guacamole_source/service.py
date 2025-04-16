
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

import guacamole

from app.datasource.base.controller import DatasourceController
from app.datasource.base.errors import HTTPDatasourceConnectionFailed

from .model import GuacamoleSource
from .schema import (
    GuacamoleRead,
    GuacamoleSessionConfig
)


class GuacamoleSourceService(DatasourceController[GuacamoleSource, GuacamoleRead]):
    '''The controller for the Guacamole datasource'''

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)
        self.model = GuacamoleSource

    def serialize(self, source: GuacamoleSource) -> GuacamoleRead:
        '''serializes the Guacamole datasource into a GuacamoleRead schema
        Arguments:
            source {GuacamoleSource} -- the Guacamole datasource
        Returns:
            GuacamoleRead -- the serialized Guacamole datasource
        '''
        return GuacamoleRead.to_model(source)

    async def connect_args(self, guac_source: GuacamoleSource) -> GuacamoleSessionConfig:
        '''returns the connection arguments for the Guacamole datasource
        Arguments:
            guac_source {GuacamoleSource} -- the Guacamole datasource
        Returns:
            GuacamoleSessionConfig -- the model representing the connection arguments
        '''
        password = await self.read_datasource_password(guac_source)  # type: ignore
        return GuacamoleSessionConfig(
            host=guac_source.endpoint,
            username=guac_source.username,
            password=password,
            data_source=guac_source.datasource
        )

    async def _try_connect(self, source: GuacamoleSource) -> Optional[guacamole.session]:
        '''creates a guacamole session from the Guacamole datasource and returns the session object
        without throwing if an error occurs
        Arguments:
            guac_source {GuacamoleSource} -- the Guacamole datasource to connect to
        Returns:
            Optional[guacamole.session] -- the guacamole session object or None if the 
            connection failed & a key error occured
        '''
        try:
            args = await self.connect_args(source)
            return guacamole.session(**args.serialize())
        except Exception:
            return None

    async def connect(self, source: GuacamoleSource) -> guacamole.session:
        '''creates a guacamole session from the Guacamole datasource
        and raises an error if the connection fails
        Arguments:
            source {GuacamoleSource} -- the Guacamole datasource to connect to

        Raises:
            HTTPDatasourceConnectionFailed: the connection failed

        Returns:
            guacamole.session -- the guacamole session object
        '''
        session = await self._try_connect(source)
        if not session:
            raise HTTPDatasourceConnectionFailed(
                f"Could not connect to Guacamole datasource {source.datasource}"
            )
        return session

    async def test_datasource_connection(self, source: GuacamoleSource) -> tuple[str | None, bool]:
        '''tests the connection to the Guacamole datasource which will throw
        if the connection fails and caught by the connect method due to a key
        error from the guacamole api wrapper

        Arguments:
            source {GuacamoleSource} -- the Guacamole datasource to connect to

        Returns:
            tuple[str | None, bool] -- the connection status
        '''
        session = await self._try_connect(source)
        if session:
            return None, True
        error = (
            'Could not establish a connection to the Guacamole datasource likely '
            'due to a misconfiguration, please try again.'
        )
        return error, False
