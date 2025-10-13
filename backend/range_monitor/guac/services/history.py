import asyncio
from datetime import UTC, datetime
from typing import AsyncGenerator, Literal

import msgspec
from fastapi.responses import StreamingResponse

from range_monitor.guac import utils as guac_utils
from range_monitor.guac.api import guac_client
from range_monitor.guac.api.dtos import HistoryEntry
from range_monitor.guac.api.spec import GuacamoleAPISpec
from range_monitor.guac.api.stream import JSONStreamReader
from range_monitor.guac.schema import (
    ConnectionsHistory,
    ConnectionTimeline,
    HistoryDataset,
    UserConnection,
)


class HistoryStruct(msgspec.Struct, forbid_unknown_fields=False):
    """
    This is camel case since, the response JSONs from Guacamole are camel case
    and msgspec does not support aliasing for fields

    """

    username: str
    remoteHost: str
    identifier: str
    uuid: str
    startDate: int
    connectionName: str | None = None
    endDate: int | None = None
    active: bool = False


async def _ndjson_history_stream(
    generator: AsyncGenerator, active_only: bool = False, since_ms: int | None = None
):
    stream_reader = JSONStreamReader(require_top_array=True)
    decoder = msgspec.json.Decoder(HistoryStruct)
    encoder = msgspec.json.Encoder()
    try:
        async for json_bytes in stream_reader.readbytes(generator):
            entry = decoder.decode(json_bytes)
            if active_only and not entry.active:
                continue

            if since_ms and entry.startDate < since_ms:
                continue

            yield encoder.encode(entry) + b'\n'
    except asyncio.CancelledError:
        raise
    except Exception:
        return


class HistoryService:
    def __init__(self, spec: GuacamoleAPISpec) -> None:
        self.spec = spec

    async def get_connections_history(
        self, connection_identifier: str
    ) -> ConnectionsHistory:
        """
        Retrieves the historical connection data for the specified
        connection identifier.

        Parameters
        ----------
        connection_identifier : str

        Returns
        -------
        ConnectionsHistory
        """
        response = await guac_client.get_connection_history(
            self.spec, connection_identifier
        )

        history: list[HistoryEntry] = []
        users: dict[str, list[int | None]] = {}

        for json_entry in response:
            entry = HistoryEntry.convert(json_entry)
            history.append(entry)
            users.setdefault(entry.username, [])

        start_dates = []
        for entry in history:
            start_dates.append(entry.start_date)

            for username, entries in users.items():
                if username == entry.username:
                    entries.append(entry.start_date)
                else:
                    entries.append(None)

        datasets: list[HistoryDataset] = [
            HistoryDataset(label=username, data=entries)
            for username, entries in users.items()
        ]

        return ConnectionsHistory(timestamps=start_dates, datasets=datasets)

    async def get_connections_timeline(self) -> ConnectionTimeline:
        """
        Retrieves a timeline of all currently active connections.

        Returns
        -------
        ConnectionTimeline
        """
        active_conn, all_conns = await asyncio.gather(
            *(
                guac_client.list_active_connections(self.spec),
                guac_client.list_connections(self.spec),
            )
        )
        active_connections = guac_utils.to_instance_list(active_conn)
        connections_map = guac_utils.get_connections_map(all_conns)

        users: list[UserConnection] = []

        for inst in active_connections:
            connection = connections_map[inst.connection_identifier]
            last_active = guac_utils.parse_guac_time(inst.start_date)
            users.append(
                UserConnection(
                    connection_name=connection.name,
                    username=inst.username,
                    identifier=connection.identifier,
                    last_active=last_active,
                )
            )

        return ConnectionTimeline(
            fetched_at=datetime.now(UTC),
            users=users,
            total=len(users),
        )

    async def stream_history(
        self,
        history_type: Literal['users', 'connections'],
        *,
        active_only: bool = False,
        since: datetime | None = None,
    ) -> StreamingResponse:
        """
        Streams either the connection history or user history as NDJSON
        due to the response size being massive.

        NOTE: The only difference in the response for connections vs users
        is the presence of the `connectionName` field in connection history.

        Parameters
        ----------
        history_type : HistoryTypes
        active_only : bool, optional
        since : datetime | None, optional

        Returns
        -------
        StreamingResponse
        """
        if history_type == 'users':
            generator = guac_client.list_users_history(self.spec)
        else:
            generator = guac_client.list_connections_history(self.spec)

        since_ms = None
        if since:
            since_ms = int(since.timestamp() * 1000)

        stream = _ndjson_history_stream(
            generator, active_only=active_only, since_ms=since_ms
        )

        return StreamingResponse(
            stream,
            status_code=200,
            media_type='application/x-ndjson',
            headers={
                'Cache-Control': 'no-cache',
            },
        )
