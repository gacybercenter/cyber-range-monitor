from collections.abc import Generator
from dataclasses import dataclass, field
from datetime import datetime
from typing import NamedTuple

import guacamole

from range_monitor.guac.dtos import (
    ActiveConnectionProfile,
    ActiveGuacamoleConnection,
    Connection,
    ConnectionInstance,
    ConnectionInstanceInfo,
    GuacamoleUser,
)


@dataclass(slots=True)
class _ConnectionInstanceContext:
    connection_id: str
    connection: Connection
    instance: ConnectionInstance


class _ConnectionContext(NamedTuple):
    connection_id: str
    connection: Connection
    active_instances: list[ActiveGuacamoleConnection] = field(default_factory=list)



@dataclass(slots=True)
class GuacamoleCollection:
    session: guacamole.session

    def iter_connections(self) -> Generator[tuple[str, Connection], None, None]:
        """
        Iterates over all connections in the Guacamole session

        Yields
        ------
        Generator[tuple[str, Connection], None, None]
        """
        all_conn_response: dict = self.session.list_connections()  # type: ignore
        for connection_id, conn in all_conn_response.items():
            yield connection_id, Connection.convert(conn)

    def _iter_active_connections(
        self,
    ) -> Generator[tuple[str, ActiveGuacamoleConnection], None, None]:
        """
        Iterates over all active connections in the Guacamole session
        returning a key-value pair of instance ID and the corresponding
        ActiveGuacamoleConnection DTO.

        Yields
        ------
        Generator[tuple[str, ActiveGuacamoleConnection], None, None]
        """
        active_conn_response: dict = self.session.list_active_connections()  # type: ignore
        for instance_id, instance in active_conn_response.keys():
            dto = ActiveGuacamoleConnection.convert(instance)
            yield instance_id, dto

    def instance_id_to_connection(self) -> dict[str, ActiveGuacamoleConnection]:
        """
        Retrieves a mapping of active instance IDs to their corresponding
        active connection details.

        Returns
        -------
        dict[str, ActiveGuacamoleConnection]
        """
        mapping: dict[str, ActiveGuacamoleConnection] = {}
        for instance_id, instance in self._iter_active_connections():
            mapping[instance_id] = instance
        return mapping

    def connection_instances(self) -> dict[str, list[ActiveGuacamoleConnection]]:
        """
        Retrieves a mapping of connection identifiers to their active instances.

        Returns
        -------
        dict[str, list[ActiveGuacamoleConnection]]
        """
        mapping: dict[str, list[ActiveGuacamoleConnection]] = {}
        for _, instance in self._iter_active_connections():
            mapping.setdefault(instance.connection_id, [])
            mapping[instance.connection_id].append(instance)
        return mapping

    def connection_map(self) -> dict[str, Connection]:
        """
        Retrieves a mapping of connection identifiers to their
        Connection DTOs.

        Returns
        -------
        dict[str, Connection]
        """
        mapping: dict[str, Connection] = {}
        for connection_id, conn in self.iter_connections():
            mapping[connection_id] = conn
        return mapping

    def _filter_context(
        self,
        context: _ConnectionContext,
        *,
        active_since: datetime | None,
        active_only: bool,
        only_protocols: set[str] | None,
    ) -> bool:
        if only_protocols and context.connection.protocol not in only_protocols:
            return False

        if active_only and not context.active_instances:
            return False

        if active_since and not any(
            datetime.fromtimestamp(inst.start_date) >= active_since
            for inst in context.active_instances
        ):
            return False

        return True

    def iter_active(self) -> Generator[_ConnectionInstanceContext, None, None]:
        all_connections = self.connection_map()

        for _, instance in self._iter_active_connections():
            if not (connection := all_connections.get(instance.connection_id)):
                continue
            instance_dto = ConnectionInstance(
                instance_id=instance.instance_id,
                start_date=instance.start_date,
                username=instance.username,
                remote_host=instance.remote_host,
            )
            yield _ConnectionInstanceContext(
                connection_id=instance.connection_id,
                connection=connection,
                instance=instance_dto,
            )

    def walk_connections(
        self,
        *,
        active_only: bool = False,
        only_protocols: set[str] | None = None,
        active_since: datetime | None = None,
    ) -> Generator[_ConnectionContext, None, None]:
        '''
        Walks through all connections, yielding contexts that
        can be filtered based on active status, protocols, and activity date.

        Parameters
        ----------
        active_only : bool, optional
            _description_, by default False
        only_protocols : set[str] | None, optional
            _description_, by default None
        active_since : datetime | None, optional
            _description_, by default None

        Yields
        ------
        Generator[_ConnectionContext, None, None]
            _description_
        '''
        connections_instances = self.connection_instances()
        filter_needed = active_only or bool(only_protocols) or bool(active_since)

        for connection_id, connection in self.iter_connections():
            context = _ConnectionContext(
                connection_id=connection_id,
                connection=connection,
            )
            if active_instances := connections_instances.get(connection_id):
                context.active_instances.extend(active_instances)

            if filter_needed and not self._filter_context(
                context,
                active_only=active_only,
                only_protocols=only_protocols,
                active_since=active_since,
            ):
                continue

            yield context
    
    def detail_connection_instance(
        self,
        context: _ConnectionInstanceContext,
        *,
        default_organization: str = 'Unassigned',
    ) -> ConnectionInstanceInfo:
        user_info = self.session.detail_user(context.instance.username)
        user_dto = GuacamoleUser.convert(user_info)

        organization = user_dto.attributes.guac_organization or default_organization

        return ConnectionInstanceInfo(
            organization=organization,
            connection=context.instance,
            user=user_dto,
        )


    def make_active_connection_profile(
        self,
        context: _ConnectionInstanceContext
    ) -> ActiveConnectionProfile:
        return ActiveConnectionProfile(
            identifier=context.connection_id,
            connection_name=context.connection.name,
            username=context.instance.username
        )



