from typing import Any
from fastapi import HTTPException, status

from sqlalchemy.ext.asyncio import AsyncSession

from .model import SaltstackSource

from ..interface.source_service_abc import DatasourceServiceABC

from .schema import (
    # SaltstackConnectionArgs,
    SaltstackOptions,
    SaltstackResponse,
)

# NOTE this class is not complete or fully implemented.


class SaltstackSourceService(DatasourceServiceABC[SaltstackSource, SaltstackResponse]):
    """The service for interacting with the SaltstackSource database model"""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(datasource_type="saltstack", model=SaltstackSource, db=db)

    async def connect_args(self, datasource: SaltstackSource) -> dict:
        """TODO implement the connection args for saltstack

        Arguments:
            datasource {SaltstackSource} -- the saltstack datasource to connect to

        Returns:
            dict -- the key word args for the saltstack datasource created from
            SaltstackConnectionArgs.
        """
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Saltstack has not been implemented yet.",
        )

    async def connect(self, datasource: SaltstackSource) -> Any:
        """TODO implement the connection to saltstack, should raise
        HTTPBadRequest if the connection fails refer to ABC for more details.

        Arguments:
            datasource {SaltstackSource} -- the saltstack datasource to connect to

        Returns:
            Any -- the connection object for saltstack
        """
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Saltstack has not been implemented yet.",
        )

    async def test_connection(
        self, datasource: SaltstackSource
    ) -> tuple[str | None, bool]:
        """TODO implement the test connection for saltstack, should not throw
        and return optional error message and a boolean for success.

        Arguments:
            datasource {SaltstackSource} -- the saltstack datasource to connect to

        Returns:
            tuple[str | None, bool] -- the error message and a boolean for success
        """
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Saltstack has not been implemented yet.",
        )

    def to_response(self, datasource: SaltstackSource) -> SaltstackResponse:
        """serializes the saltstack datasource into the key word arguments
        to create the response model

        Arguments:
            datasource {SaltstackSource} -- the saltstack datasource to serialize

        Returns:
            dict -- the key word arguments to create the response model
        """
        base_schema = self.get_base_schema(datasource)
        options = SaltstackOptions(hostname=datasource.hostname)
        return SaltstackResponse(data_source=base_schema, options=options)
