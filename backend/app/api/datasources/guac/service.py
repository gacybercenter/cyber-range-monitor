import guacamole
from sqlalchemy.ext.asyncio import AsyncSession


from app.common.errors import HTTPBadRequest

from ..interface.source_service_abc import DatasourceServiceABC
from .model import GuacamoleSource


from .schema import GuacSessionParams, GuacOptions, GuacResponse


class GuacamoleSourceService(DatasourceServiceABC[GuacamoleSource, GuacResponse]):
    """The service for the Guacamole datasource"""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(datasource_type="guacamole", model=GuacamoleSource, db=db)

    async def connect_args(self, datasource: GuacamoleSource) -> dict:
        """creates the key word arguments to create a guacamole.session instance
        given a datasource

        Arguments:
            datasource {GuacamoleSource} -- the Guacamole datasource to connect to

        Returns:
            dict -- the key word arguments to create a guacamole.session instance
        """
        password = await self.models.read_password(datasource)
        return GuacSessionParams(
            host=datasource.endpoint,
            username=datasource.username,
            password=password,
            data_source=datasource.datasource,
        ).serialize()

    async def _try_connect(self, source: GuacamoleSource) -> guacamole.session | None:
        """creates a guacamole session from the Guacamole datasource and returns the session object
        without throwing if an error occurs
        Arguments:
            guac_source {GuacamoleSource} -- the Guacamole datasource to connect to
        Returns:
            Optional[guacamole.session] -- the guacamole session object or None if the
            connection failed & a key error occured
        """
        try:
            args = await self.connect_args(source)
            return guacamole.session(**args)
        except Exception:
            return None

    async def connect(self, source: GuacamoleSource) -> guacamole.session:
        """creates a guacamole session from the Guacamole datasource and returns the session object
        without throwing if an error occurs
        Arguments:
            guac_source {GuacamoleSource} -- the Guacamole datasource to connect to
        Raises:
            HTTPBadRequest: if the connection failed & a key error occured
        Returns:
            Optional[guacamole.session] -- the guacamole session object or None if the
            connection failed & a key error occured
        """
        session = await self._try_connect(source)
        if not session:
            raise HTTPBadRequest("Failed to connect to Guacamole datasource")

        return session

    async def test_connection(self, source: GuacamoleSource) -> tuple[str | None, bool]:
        """tests the connection to the datasource and returns the session object
        Arguments:
            guac_source {GuacamoleSource} -- the Guacamole datasource to connect to
        Returns:
            Optional[guacamole.session] -- the guacamole session object or None if the
            connection failed & a key error occured
        """
        session = await self._try_connect(source)
        if session:
            return None, False

        error = (
            "Could not establish a connection to the Guacamole datasource likely "
            "due to a misconfiguration, please update the datasource and try again."
        )
        return error, False

    def to_response(self, datasource: GuacamoleSource) -> GuacResponse:
        """serializes the datasource to a response object
        Arguments:
            guac_source {GuacamoleSource} -- the Guacamole datasource to connect to
        Returns:
            dict -- the key word arguments to create a response model
        """
        options = GuacOptions(
            datasource=datasource.datasource,
        )
        return GuacResponse(
            data_source=self.get_base_schema(datasource), options=options
        )
