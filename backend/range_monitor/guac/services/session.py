Annotated[
        list[str] | None,
        Query(
            None,
            description='Filter connections by protocol(s)',
            example=['rdp', 'vnc'],
        ),
    ]import base64
from dataclasses import dataclass, field
from datetime import datetime
from typing import Self

import guacamole

from range_monitor.errors import BadRequest
from range_monitor.guac.schema import (
    ConnectionUrlEnvelope,
    GuacamoleActiveInstances,
    GuacamoleConnectionList,
    KilledConnectionsResults,
)

from .backend import GuacamoleCollection


@dataclass(slots=True)
class GuacamoleSessionService:
    session: guacamole.session
    _collection: GuacamoleCollection = field(init=False)

    @classmethod
    def create(
        cls,
        session: guacamole.session
    ) -> Self:
        self = cls(session=session)
        self._collection = GuacamoleCollection(session=session)
        return self

    def get_active_instances(self) -> GuacamoleActiveInstances:

        connected_usernames = set()
        instances: dict = {}
        profiles = []
        for instance_data in self._collection.iter_active():
            instance_details = self._collection.detail_connection_instance(instance_data)
            instance_profile = self._collection.make_active_connection_profile(
                instance_data
            )

            oragnization = instance_details.organization or 'default'
            instances.setdefault(oragnization, []).append(instance_details)
            profiles.append(instance_profile)
            connected_usernames.add(instance_profile.username)

        return GuacamoleActiveInstances(
            connected_usernames=list(connected_usernames),
            instances=instances,
            profiles=profiles,
        )

    def _urlencode_token(self, identifier: str, mode: str) -> str:
        raw = f'{identifier}\u0000{mode}\u0000{self.session.data_source}'.encode(
            'utf-8', 'strict'
        )
        return base64.b64encode(raw).decode('ascii').rstrip('=')


    def get_connection_url(
        self,
        connection_identifiers: list[str]
    ) -> ConnectionUrlEnvelope:
        '''
        Generates a connectable URL "envelope" for all of the provided connection
        identifiers.

        - If a connection has one or more active sessions, the oldest active sessions
        uuid (i.e identifier) will be used in the URL in 'a' (active) mode.

        - If a connection does not have any active sessions, the connection identifier
        will be used in the URL in the 'c' (connection).


        Parameters
        ----------
        connection_identifiers : list[str]

        Returns
        -------
        ConnectionUrlEnvelope

        Raises
        ------
        BadRequest
        '''

        if not connection_identifiers:
            raise BadRequest('No connection identifiers provided.')


        parts = []
        active_connections = self._collection.connection_instances()
        for connection_id in connection_identifiers:
            if not (instances := active_connections.get(connection_id)):
                encoded_token = self._urlencode_token(connection_id, 'c')
                parts.append(encoded_token)
                continue

            oldest_instance = min(instances, key=lambda i: i.start_date)
            encoded_token = self._urlencode_token(oldest_instance.instance_id, 'a')
            parts.append(encoded_token)

        url_path = '.'.join(parts)
        connectable_url = f'{self.session.host}/#/client/{url_path}'

        return ConnectionUrlEnvelope(
            connectable_url=connectable_url,
            active_connections=active_connections,
        )

    def kill_connection_identifiers(
        self,
        connection_identifiers: list[str]
    ) -> KilledConnectionsResults:
        if not connection_identifiers:
            raise BadRequest('No connection identifiers provided.')

        active_connections = self._collection.connection_instances()

        results = KilledConnectionsResults()
        for connection_id in connection_identifiers:
            if not (to_kill := active_connections.get(connection_id)):
                results.add_ignored(connection_id)
                continue

            results.extend_kill_list([conn.instance_id for conn in to_kill])

        response = {}
        try:
            response: dict = self.session.kill_active_connections(
                results.connections.killed
            ) # type: ignore
        except Exception:
            results.succes = False
            results.total_killed = 0

        results.guacamole_response = response

        return results

    def get_connections(self, only_protocols: set[str] | None, active_since: datetime | None) -> GuacamoleConnectionList:
        response = GuacamoleConnectionList()

        active: dict[str, list] = {}
        for context in self._collection.walk_connections(
            only_protocols=only_protocols,
            active_since=active_since,
            active_only=False,
        ):
            response.connections.append(context.connection)

            id = context.connection.identifier
            active.setdefault(id, [])
            if instances := context.active_instances:
                active[id].extend(instances)

        response.total = len(response.connections)
        response.active_connections = active
        return response

