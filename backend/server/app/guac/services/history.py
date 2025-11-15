import asyncio
from collections.abc import AsyncGenerator
from datetime import UTC, datetime
from typing import Literal

import msgspec
from fastapi.responses import StreamingResponse

from server.app.guac import utils as guac_utils
from server.app.guac.client import operations
from server.app.guac.client.daos import HistoryEntry
from server.app.guac.client.spec import GuacamoleAPISpec
from server.app.guac.client.stream import JSONStreamReader
from server.app.guac.schema import (
    ConnectionsHistory,
    ConnectionTimeline,
    HistoryDataset,
    UserConnection,
)


class HistoryStruct(msgspec.Struct, forbid_unknown_fields=False):
    username: str
    remoteHost: str  # noqa: N815
    identifier: str
    uuid: str
    startDate: int  # noqa: N815
    connectionName: str | None = None  # noqa: N815
    endDate: int | None = None  # noqa: N815
    active: bool = False


async def _ndjson_history_stream(
    generator: AsyncGenerator, *, active_only: bool = False, since_ms: int | None = None
) -> AsyncGenerator[bytes]:
    """
    Streams history entries as NDJSON from the provided generator,
    filtering by active_only and since_ms if provided.
    """
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
            The connection identifier to retrieve history for.

        Returns
        -------
        ConnectionsHistory
        """
        response = await operations.get_connection_history(
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
        active_conn, all_conns = await asyncio.gather(*(
            operations.list_active_connections(self.spec),
            operations.list_connections(self.spec),
        ))
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
            The type of history to stream, either 'users' or 'connections'.
        active_only : bool, optional
            Whether to only include active connections, by default False.
        since : datetime | None, optional
            If provided, only history entries since this time are included,
            by default None.

        Returns
        -------
        StreamingResponse
        """
        if history_type == 'users':
            generator = operations.list_users_history(self.spec)
        else:
            generator = operations.list_connections_history(self.spec)

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
