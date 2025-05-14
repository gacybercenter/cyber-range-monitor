import asyncio

import json
import time
from typing import Annotated, Any, Literal

from fastapi import WebSocket
from .schema import LogEntry, LogFilter, CustomBaseModel


from pydantic import Field


class ClientMeta(CustomBaseModel):
    logs_sent: Annotated[
        int, Field(default=0, description="The number of logs sent to the client.")
    ] = 0
    commands_recieved: Annotated[
        int,
        Field(
            default=0, description="The number of commands received from the client."
        ),
    ] = 0
    errors: Annotated[
        int,
        Field(default=0, description="The number of errors encountered by the client."),
    ] = 0


class ClientState(CustomBaseModel):
    connected: Annotated[
        bool,
        Field(default=False, description="Whether the client is connected or not."),
    ] = False

    paused: Annotated[
        bool, Field(default=False, description="Whether the client is paused or not.")
    ] = False

    last_activity: Annotated[
        float,
        Field(
            default_factory=lambda: time.time(),
            description="The last time the client pinged the server.",
        ),
    ] = time.time()

    client_id: Annotated[str, Field(..., description="The client ID of the client.")]
    meta: Annotated[
        ClientMeta,
        Field(default=ClientMeta(), description="The metadata for the client."),
    ] = ClientMeta()

    filter: Annotated[
        LogFilter | None, Field(default=None, description="The filter for the client.")
    ] = None

    def update_meta(
        self, type: Literal["logs_sent", "commands_recieved", "errors"]
    ) -> None:
        if type == "logs_sent":
            self.meta.logs_sent += 1
        elif type == "commands_recieved":
            self.meta.commands_recieved += 1
        elif type == "errors":
            self.meta.errors += 1
        else:
            raise ValueError(f"Invalid type: {type}")
        self.update_activity()

    def can_send(self, entry: LogEntry) -> bool:
        """Checks if the client can send logs.

        Returns:
            bool: Whether the client can send logs or not.
        """
        status_allows = self.connected and not self.paused
        filter_allows = self.filter is None or (
            self.filter and self.filter.matches_entry(entry)
        )
        return status_allows and filter_allows

    def update_activity(self) -> None:
        """Updates the last activity time of the client.

        Returns:
            None
        """
        self.last_activity = time.time()


class LogSocketClient:
    def __init__(
        self,
        *,
        client_id: str,
        websocket: WebSocket,
        filter: LogFilter | None,
    ) -> None:
        self.web_socket: WebSocket = websocket
        self.state: ClientState = ClientState(client_id=client_id, filter=filter)

    async def send_log(self, entry: LogEntry) -> bool:
        """Sends a log entry to the client.

        Args:
            entry (LogEntry): The log entry to send.
        """
        if not self.state.can_send(entry):
            return False

        filters = self.state.filter.serialize() if self.state.filter else None
        data_response = {
            "client_id": self.state.client_id,
            "log_entry": entry.serialize(),
            "filter": filters,
            "status": "DATA",
        }

        try:
            await self.web_socket.send_json(data_response)
            self.state.update_meta("logs_sent")
            return True
        except Exception as e:
            self.state.connected = False
            self.state.update_meta("errors")
            return False

    async def update_filter(self, filter: LogFilter) -> None:
        """Updates the filter for the client.

        Args:
            filter (LogFilter): The new filter for the client.
        """
        self.state.filter = filter
        await self._send_client("FILTER-RECIEVED")
        self.state.update_meta("commands_recieved")

    async def set_paused(self, paused: bool) -> None:
        """Sets the paused state of the client.

        Args:
            paused (bool): Whether to pause the client or not.
        """
        self.state.paused = paused
        await self._send_client("PAUSED" if paused else "RESUMED")
        self.state.update_meta("commands_recieved")

    async def ping(self) -> bool:
        """Pings the client to check if it is still connected.

        Returns:
            bool: Whether the client is still connected or not.
        """

        return await self._send_client("PING")

    async def send_error(self, error: str) -> bool:
        """Sends an error message to the client.

        Args:
            error (str): The error message to send.
        """

        return await self._send_client("ERROR", error=error)

    async def _send_client(self, status: str, *, error: str | None = None) -> bool:
        if not self.state.connected:
            return False

        client_msg = self.state.serialize()
        client_msg["status"] = status
        if error:
            client_msg["error"] = error

        try:
            await self.web_socket.send_json(client_msg)
            self.state.update_activity()
            return True
        except Exception as e:
            self.state.connected = False
            self.state.update_meta("errors")
            return False

    def is_stale(self, max_idle: int) -> bool:
        """Checks if the client is stale.

        Args:
            max_idle (int): The maximum idle time in seconds.

        Returns:
            bool: Whether the client is stale or not.
        """
        return time.time() - self.state.last_activity > max_idle
