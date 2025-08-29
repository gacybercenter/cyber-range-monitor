import guacamole
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from range_monitor.errors import HTTPUnprocessableEntity

from .repo import GuacamoleRepo


class GuacamoleSessionAdapter:
    def __init__(self, session: AsyncSession) -> None:
        self.repo: GuacamoleRepo = GuacamoleRepo(session)

    def make_session(self, params: dict) -> guacamole.session | None:
        """
        Create a Guacamole connection using the provided parameters.

        Parameters
        ----------
        params : dict
            Parameters required to create the Guacamole connection.

        Returns
        -------
        guacamole.session | None
            The created Guacamole session or None if creation fails.
        """
        params['data_source'] = params.pop('source_type')
        try:
            return guacamole.session(**params)
        except Exception:
            return None

    def test_connection(self, params: dict) -> bool:
        """
        Test the Guacamole connection with the provided parameters.

        Parameters
        ----------
        params : dict
            Parameters required to test the Guacamole connection.

        Returns
        -------
        bool
            True if the connection is successful, False otherwise.
        """
        return self.make_session(params) is not None

    def _invalid_enabled_source(self) -> HTTPException:
        return HTTPUnprocessableEntity(
            'The enabled Guacamole datasource is not set or is invalid.'
        )

    async def connect(self, datasource_id: str) -> guacamole.session:
        if not (datasource := await self.repo.get_connection_params()):
            raise self._invalid_enabled_source()

        connection = self.make_session(datasource)

        if not connection:
            raise self._invalid_enabled_source()

        return connection


    async def connect_by_id(self, datasource_id: str) -> guacamole.session:
        if not (params := await self.repo.get_connection_params(datasource_id)):
            raise self._invalid_enabled_source()

        if not (connection := self.make_session(params)):
            raise self._invalid_enabled_source()

        return connection
