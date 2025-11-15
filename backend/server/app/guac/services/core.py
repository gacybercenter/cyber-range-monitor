import asyncio

from server.app.guac import utils as guac_utils
from server.app.guac.client import operations
from server.app.guac.client.daos import GuacUser
from server.app.guac.client.spec import GuacamoleAPISpec
from server.app.guac.schema import (
    ActiveOrganization,
    ConnectedOrganization,
    ConnectionActivity,
    GuacamoleSummary,
    GuacUrlScheme,
    UserConnection,
)
from server.app.guac.services.history import HistoryService
from server.app.guac.services.topology import TopologyService

"""TODO


[DONE] Implement streaming for api operation (see operations.py) for
`list_users_history` and `list_connections_history`, StreamingResponse
that yields the items for the frontend to consume individually, response
size for the individual requests is MASSIVE (40k+ entries)

- Individual routes for fetching details about the individual connections
and routes to fetch as needed for the frontend

- Caching strategy for topology, fetch one, if diff, only include edited, accept
some query param or header to check a cache of a hash for each, leverage msgspec
and redis

"""


class GuacamoleRestService:
    """
    The main service for interacting with the Guacamole RESTful API
    containing sub services for topology and history.
    """

    def __init__(self, spec: GuacamoleAPISpec) -> None:
        self.spec = spec
        self.topology = TopologyService(self.spec)
        self.history = HistoryService(self.spec)

    async def get_summary(self) -> GuacamoleSummary:
        """
        Retrieves a summary of the connected Guacamole server

        Returns
        -------
        GuacamoleSummary
        """
        response = await operations.get_self(self.spec)
        attributes: dict = response.get('attributes', {})
        hostname = self.spec.base_url

        last_active_raw = response.get('lastActive', None)

        last_active_dt = guac_utils.parse_guac_time(last_active_raw)

        active_connections = await operations.list_active_connections(self.spec)

        connected_org = ConnectedOrganization(
            name=attributes.get('guac-organization') or 'Unknown',
            role=attributes.get('guac-organization-role') or 'Unknown',
        )

        return GuacamoleSummary(
            username=response['username'],
            last_active=last_active_dt,
            hostname=hostname,
            organization=connected_org,
            active_connections=len(active_connections),
        )

    async def get_connection_activity(self) -> ConnectionActivity:
        """
        Retrieves an overview of the current connection activity.

        Returns
        -------
        ConnectionActivity
        """
        response = await operations.list_active_connections(self.spec)

        active_connections = guac_utils.to_instance_map(response)

        active_users = await asyncio.gather(
            *(
                operations.get_user(self.spec, conn.username)
                for conn in active_connections.values()
            )
        )

        organizations: dict[str, ActiveOrganization] = {}
        running_total = 0

        for user_response in active_users:
            user = GuacUser.convert(user_response)
            org_name = user.attributes.guac_organization or 'Unknown'

            org = organizations.setdefault(org_name, ActiveOrganization(name=org_name))

            last_active = guac_utils.parse_guac_time(user.last_active)
            org.connections[user.username] = UserConnection(
                identifier=user.username,
                connection_name=user.attributes.guac_full_name or 'Unknown',
                username=user.attributes.guac_email_address or 'Unknown',
                last_active=last_active,
            )

            org.total += 1
            running_total += 1

        return ConnectionActivity(
            total_active=running_total,
            organizations=organizations,
            instances=list(active_connections.values()),
        )

    async def get_connection_url(self, connection_ids: list[str]) -> GuacUrlScheme:
        """
        Generates a Guacamole URL that can be used to connect to one or more
        connections or active instances. The oldest active instance for each
        connection is preferred, otherwise the connection itself is used.

        Parameters
        ----------
        connection_ids : list[str]
            A list of connection identifiers to include in the URL.

        Returns
        -------
        str
            A URL that can be used to connect to the specified connections
            or active instances.
        """
        response = await operations.list_active_connections(self.spec)

        oldest = guac_utils.map_instances_by_oldest(response)

        parts = []
        for conn_id in connection_ids:
            if oldest_instance := oldest.get(conn_id):
                part = guac_utils.guac_urlencode(
                    identifier=oldest_instance.identifier,
                    char='a',
                    data_source=self.spec.data_source,
                )
            else:
                part = guac_utils.guac_urlencode(
                    identifier=conn_id, char='c', data_source=self.spec.data_source
                )
            parts.append(part)

        parts_path = '.'.join(parts)
        url = f'{self.spec.client.base_url}/#/client/{parts_path}'

        return GuacUrlScheme(url=url, token=self.spec.client_token)

    async def kill_identifiers(self, identifiers: list[str]) -> None:
        """
        Kills the specified active connection instances.

        Parameters
        ----------
        identifiers : list[str]
            A list of active connection instance identifiers to kill.

        Returns
        -------
        None
        """
        await operations.kill_connections(self.spec, identifiers)
