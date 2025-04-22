

import guacamole
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import GuacamoleSource
from app.core.datasources.service import DatasourceServiceABC

from app.core.errors import HTTPBadRequest


from .schema import (
    GuacamoleConnectionArgs,
    GuacamoleOptions,
    GuacamoleCreate,
    GuacamoleOptionsUpdate,
    GuacamoleUpdate,
    GuacamoleResponse
)


class GuacamoleSourceService(DatasourceServiceABC[
    GuacamoleSource, GuacamoleCreate, GuacamoleUpdate
]):
    """The service for the Guacamole datasource"""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(GuacamoleSource, db)

    def validate_create_schema(self, req_body: dict) -> GuacamoleCreate:
        """validates the schema of the options for a guacamole datasource
        Returns:
            dict -- the request body with the options serialized
        """
        opts = req_body.pop('options')
        if not opts:
            raise HTTPBadRequest(
                "Options must be provided to create this datasource."
            )
        options = GuacamoleOptions.model_validate(opts)

        return GuacamoleCreate(
            **req_body,
            options=options
        )

    def validate_update_schema(self, req_body: dict) -> GuacamoleUpdate:
        """validates the update schema / options for the datasource
        ensuring valid data is provided
        Arguments:
            options {GuacamoleOptionsUpdate} -- the request model after .serialize()
        Returns:
            dict -- the validated request body with the options properly formatted
        """
        opts = req_body.pop('options')
        if not opts:
            return GuacamoleUpdate(**req_body)

        options = GuacamoleOptionsUpdate.model_validate(opts)
        return GuacamoleUpdate(
            **req_body,
            options=options
        )

    async def connect_args(self, datasource: GuacamoleSource) -> dict:
        '''creates the key word arguments to create a guacamole.session instance
        given a datasource

        Arguments:
            datasource {GuacamoleSource} -- the Guacamole datasource to connect to

        Returns:
            dict -- the key word arguments to create a guacamole.session instance
        '''
        password = await self.models.read_password(datasource)
        return GuacamoleConnectionArgs(
            host=datasource.endpoint,
            username=datasource.username,
            password=password,
            data_source=datasource.datasource
        ).serialize()

    async def _try_connect(self, source: GuacamoleSource) -> guacamole.session | None:
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
            return guacamole.session(**args)
        except Exception:
            return None

    async def connect(self, source: GuacamoleSource) -> guacamole.session:
        '''creates a guacamole session from the Guacamole datasource and returns the session object
        without throwing if an error occurs
        Arguments:
            guac_source {GuacamoleSource} -- the Guacamole datasource to connect to
        Raises:
            HTTPBadRequest: if the connection failed & a key error occured
        Returns:
            Optional[guacamole.session] -- the guacamole session object or None if the 
            connection failed & a key error occured
        '''
        session = await self._try_connect(source)
        if not session:
            raise HTTPBadRequest('Failed to connect to Guacamole datasource')

        return session

    async def test_connection(self, source: GuacamoleSource) -> tuple[str | None, bool]:
        '''tests the connection to the datasource and returns the session object
        Arguments:
            guac_source {GuacamoleSource} -- the Guacamole datasource to connect to
        Returns:
            Optional[guacamole.session] -- the guacamole session object or None if the 
            connection failed & a key error occured
        '''
        session = await self._try_connect(source)
        if session:
            return None, False

        error = (
            'Could not establish a connection to the Guacamole datasource likely '
            'due to a misconfiguration, please update the datasource and try again.'
        )
        return error, False

    def to_response(self, datasource: GuacamoleSource) -> GuacamoleResponse:
        '''serializes the datasource to a response object
        Arguments:
            guac_source {GuacamoleSource} -- the Guacamole datasource to connect to
        Returns:
            dict -- the key word arguments to create a response model
        '''
        kwargs = {
            **self.get_base_args(datasource),
            'options': {
                'datasource': datasource.datasource
            }
        }
        return GuacamoleResponse(**kwargs)
