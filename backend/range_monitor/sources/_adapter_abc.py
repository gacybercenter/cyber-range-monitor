import abc
from typing import Generic, NamedTuple, TypeVar

D = TypeVar('D')
C = TypeVar('C')


class ConnectionTestDetail(NamedTuple):
    success: bool
    error: str | None


class APISourceAdapter(abc.ABC, Generic[D, C]):
    """
    An abstract base class defining the interface for
    datasource adapters.

    Parameters
    ----------
    Generics :
        D : The datasource schema type.
        C : The connection type (e.g `httpx.AsyncClient`)
    """

    @abc.abstractmethod
    async def connect(self, datasource: D, password: str) -> C:
        """
        Establishes and returns a connection to the datasource.

        Parameters
        ----------
        datasource : D
        password : str

        Returns
        -------
        C
        """

    @abc.abstractmethod
    async def test_connection(
        self, datasource: D, password: str
    ) -> ConnectionTestDetail:
        """
        Tests the connection to the datasource using the provided
        datasource details and password.

        Parameters
        ----------
        datasource : D
        password : str

        Returns
        -------
        bool
        """

    @abc.abstractmethod
    async def close_connection(self) -> None:
        """
        Closes the current connection to the datasource.
        """

    @abc.abstractmethod
    async def get_connection(self) -> C | None:
        """
        Retrieves the current connection if it exists.

        Returns
        -------
        C | None
        """
