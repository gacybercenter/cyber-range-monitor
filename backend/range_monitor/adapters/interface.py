






import abc


class ConnectableAdapter(abc.ABC):
    @abc.abstractmethod
    async def connect(self) -> None:
        """Establish a connection to the resource."""
        pass

    @abc.abstractmethod
    async def disconnect(self) -> None:
        """Close the connection to the resource."""
        pass

    @abc.abstractmethod
    def is_open(self) -> bool:
        """Check if the connection to the resource is open."""
        pass

    @abc.abstractmethod
    async def open(self, **kwargs) -> None:
        """Open the connection to the resource with optional parameters."""
        pass