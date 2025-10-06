import base64
import dataclasses as dc
import os
import pprint
import time
from pathlib import Path
from typing import Iterable, Self

import guacamole
from pydantic import BaseModel, ConfigDict, Field


def to_camel_case(string: str) -> str:
    """
    Pydantic alias generator to convert snake_case to camelCase
    when `model_dump()` is called which automatically makes snake
    case to camel case conversions for keys in dicts.
    """
    words = string.split('_')
    new_name = []
    for i, word in enumerate(words):
        if i:
            new_name.append(word.capitalize())
        else:
            new_name.append(word.lower())

    return ''.join(new_name).replace('Id', 'Id')


def kebab_to_snake(string: str) -> str:
    return string.replace('-', '_')


class GuacamoleDTO(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel_case,
        populate_by_name=True,
    )

    def pprint(self) -> None:
        pprint.pprint(self.model_dump())


class ActiveGuacamoleConnection(GuacamoleDTO):
    """
    Represents a single active connection in Guacamole
    returned from list_active_connections()

    Parameters
    ----------
    GuacamoleDTO
    """

    connectable: bool
    connection_identifier: str
    identifier: str
    start_date: int
    username: str
    remote_host: str

    def is_older(self, other_start_date: int) -> bool:
        return self.start_date < other_start_date


class ConnectionAttributes(GuacamoleDTO):
    """
    Represents the attributes of a connection group in
    Guacamole, there are more but these are the consistent
    ones that are worth modeling.
    """

    model_config = ConfigDict(
        alias_generator=kebab_to_snake,
    )

    max_connections: int | None = None
    max_connections_per_user: int | None = None
    weight: int | None = None
    failover_only: bool | None = None
    guacd_hostname: str | None = None
    guacd_port: int | None = None


class GuacamoleConnection(GuacamoleDTO):
    """
    Represents a single connection in Guacamole,
    it's returned from multiple api calls.
    """

    identifier: str
    active_connections: int
    name: str
    parent_identifier: str | None = None
    protocol: str
    last_active: int | None = None
    attributes: ConnectionAttributes


class ConnectionGroupAttributes(GuacamoleDTO):
    model_config = ConfigDict(
        alias_generator=kebab_to_snake,
    )

    max_connections: int | None = None
    max_connections_per_user: int | None = None
    enable_session_affinity: bool | None = None


class ConnectionGroup(GuacamoleDTO):
    """
    Represents a connection group in Guacamole,
    returned from list_connection_groups()
    """

    active_connections: int
    attributes: ConnectionAttributes
    parent_identifier: str | None = None
    group_type: str = Field(alias='type')
    identifier: str
    name: str

    @classmethod
    def list_groups(cls, sess: guacamole.session) -> list[Self]:
        raw_groups: dict = sess.list_connection_groups()  # type: ignore
        return [cls.model_validate(group) for group in raw_groups.values()]


class ActiveConnectionProfile(GuacamoleDTO):
    identifier: str
    connection_name: str
    username: str


class UserDetailAttributes(GuacamoleDTO):
    """
    From detail_user()
    """

    model_config = ConfigDict(
        alias_generator=kebab_to_snake,
        populate_by_name=True,
    )
    guac_email_address: str | None = None
    guac_full_name: str | None = None
    guac_organization: str | None = None
    guac_organization_role: str | None = None


class ActiveGuacamoleUser(GuacamoleDTO):
    """
    From detail_user()
    """

    attributes: UserDetailAttributes
    last_active: int | None = None
    username: str



"""
list_active_connections
list_connections
list_connection_group_connections
kill_active_connections
detail_connection

{
    "root": {
        "name": ...,
        "identifier": ...,
        "type_": ...,
        "active_connections": ...,
    },
    "connection_groups": {
        "<identifier>": {
            "name": ...,
            "identifier": ...,
            "type_": ...,
            "active_connections": ...,
            "total_connections": ...,
            "attributes": {
                "max_connections": ...,
                "max_connections_per_user": ...,
            }
        }
        ....
    },
    "connections": {
        "<parent_identifier>": [ <GuacamoleConnection>, ... ],
    },
    total_connections: int
    total_active_connections: int
}

"""


@dc.dataclass(slots=True)
class GuacamoleSessionService:
    session: guacamole.session

    # list_active_connections()
    def get_active_connections(self) -> list[ActiveGuacamoleConnection]:
        active_conn_response: dict = self.session.list_active_connections()  # type: ignore
        return [
            ActiveGuacamoleConnection.model_validate(conn)
            for conn in active_conn_response.values()
        ]

    # list_connections()
    def get_all_connections(self) -> list[GuacamoleConnection]:
        all_conn_response: dict = self.session.list_connections()  # type: ignore
        return [
            GuacamoleConnection.model_validate(conn)
            for conn in all_conn_response.values()
        ]

    # list_connection_groups()
    def get_connection_group_list(self) -> list[ConnectionGroup]:
        conn_group_response: dict = self.session.list_connection_groups()  # type: ignore
        return [
            ConnectionGroup.model_validate(group)
            for group in conn_group_response.values()
        ]

    # get_active_users()
    def get_active_users(self) -> dict[str, ActiveGuacamoleUser]:
        raw_active_connections: dict = self.session.list_active_connections()  # type: ignore
        users: dict[str, ActiveGuacamoleUser] = {}
        for conn in raw_active_connections.values():
            if 'username' not in conn or not (username := conn['username']):
                continue
            user_detail = self.session.detail_user(username)  # type: ignore
            users[username] = ActiveGuacamoleUser.model_validate(user_detail)

        return users

    # get_active_conns()
    def list_active_connection_profiles(self) -> list[ActiveConnectionProfile]:
        all_connections: dict = self.session.list_connections()  # type: ignore
        all_ids_list = all_connections.keys()
        active_connections: dict = self.session.list_active_connections()  # type: ignore
        profiles: list[ActiveConnectionProfile] = []
        for active in active_connections.values():
            active_id = active['connectionIdentifier']
            if active_id not in all_ids_list:
                continue
            active_entry = all_connections[active_id]
            profiles.append(
                ActiveConnectionProfile(
                    identifier=active['identifier'],
                    connection_name=active_entry['name'],
                    username=active['username'],
                )
            )

        return profiles

    def _urlencode_token(self, identifier: str, mode: str) -> str:
        raw = f'{identifier}\u0000{mode}\u0000{self.session.data_source}'.encode(
            'utf-8', 'strict'
        )
        return base64.b64encode(raw).decode('ascii').rstrip('=')


    def _oldest_instance_for(
        self,
        instances: Iterable['ActiveGuacamoleConnection'],
        conn_identifier: str,
    ) -> ActiveGuacamoleConnection | None:
        matches = [i for i in instances if i.connection_identifier == conn_identifier]
        if not matches:
            return None

        return min(matches, key=lambda i: i.start_date)



    def build_connectable_url(self, connection_identifiers: list[str]):
        if not connection_identifiers:
            return self.session.host

        active_instances = self.get_active_connections()
        parts: list[str] = []

        for conn_id in connection_identifiers:
            oldest = self._oldest_instance_for(active_instances, conn_id)
            if oldest:
                parts.append(self._urlencode_token(oldest.identifier, 'a'))
            else:
                parts.append(self._urlencode_token(conn_id, 'c'))

        path = ".".join(parts)
        return f"{self.session.host}/#/client/{path}"

    def kill_connection_identifiers(self, connection_identifiers: list[str]) -> bool:
        if not connection_identifiers:
            return False

        active_instances = self.get_active_connections()
        to_kill = [
            inst.identifier
            for inst in active_instances
            if inst.connection_identifier in connection_identifiers
        ]
        try:
            self.session.kill_active_connections(to_kill)
        except Exception:
            return False

        return True




class ConnectionHistoryEntry(GuacamoleDTO):
    active: bool
    connection_identifier: str
    connection_name: str
    end_date: int | None = None
    identifier: str
    remote_host: str
    sharing_profile_identifier: str | None = None
    sharing_profile_name: str | None = None
    start_date: int
    username: str
    uuid: str


class ConnectionHistoryDataset(GuacamoleDTO):
    username: str
    elapsed_intervals: list[int] = Field(default_factory=list)


class ConnectionHistory(GuacamoleDTO):
    timestamps: list[int]
    dataset: list[ConnectionHistoryDataset]

    @classmethod
    def from_entries(cls, entries: list[ConnectionHistoryEntry]):
        timestamps = []

        datasets: dict[str, ConnectionHistoryDataset] = {
            entry.username: ConnectionHistoryDataset(username=entry.username)
            for entry in entries
        }

        for entry in entries:
            if entry.end_date is None:
                entry.end_date = round(time.time() * 1000)
            timestamps.append(entry.start_date)
            elapsed = entry.end_date - entry.start_date


class Startup:
    @staticmethod
    def load_credentials() -> dict:
        env_contents = Path('.env').read_text().splitlines()

        creds = {}
        for line in env_contents:
            key, value = line.split('=', 1)
            creds[key] = value

        return creds

    @staticmethod
    def get_guacamole_session() -> guacamole.session:
        os.chdir(Path(__file__).parent)

        print('CWD:', os.getcwd())
        creds = Startup.load_credentials()
        return guacamole.session(**creds)


def test_guacamole_service() -> None:
    sess = Startup.get_guacamole_session()
    service = GuacamoleSessionService(sess)
    print('get_active_connections:')
    pprint.pprint(service.get_active_connections())
    #  pass
    print('get_all_connections:')
    pprint.pprint(service.get_all_connections())
    # pass
    print('get_connection_group_list:')
    pprint.pprint(service.get_connection_group_list())
    # pass
    print('get_connection_group_connections:')

def test_connection_history() -> None:
    sess = Startup.get_guacamole_session()
    for conn in sess.list_active_connections().values():  # type: ignore
        history: list = get_connection_history(sess, conn['connectionIdentifier'])  # type: ignore
        for raw_entry in history:
            entry = ConnectionHistoryEntry.model_validate(raw_entry)
            entry.pprint()
            input()


def get_connection_history(sess: guacamole.session, guac_id: str) -> None:
    return sess.detail_connection(guac_id, 'history')  # type: ignore


@dc.dataclass
class Connection:
    active_connections: int
    identifier: str
    name: str
    parent_identifier: str | None = None
    connection_type: str | None = None

    @property
    def weight_name(self) -> str:
        if self.identifier == 'ROOT':
            return self.name

        if self.connection_type:
            return 'connection group'

        return f'{self.name} ({self.active_connections} active)'


def extract_connections(obj: object) :
    conns = []
    active_conn_sum = 0

    stack = [obj]

    while stack:
        current = stack.pop()

        if isinstance(current, dict):
            if current.get('name') and current.get('identifier'):
                conn = current.copy()
                conn['activeConnections'] = int(conn['activeConnections'])

                if groups := conn.pop('childConnectionGroups', None):
                    stack.append(groups)

                if child_conn := conn.pop('childConnections', None):
                    stack.append(child_conn)

                conns.append(Connection(
                    active_connections=conn.get('activeConnections', 0),
                    identifier=conn.get('identifier', ''),
                    name=conn.get('name', ''),
                    parent_identifier=conn.get('parentIdentifier'),
                    connection_type=conn.get('type'),
                ))
                active_conn_sum += conn.get('activeConnections', 0)

            else:
                for value in current.values():
                    if isinstance(value, (dict, list)):
                        stack.append(value)

        elif isinstance(current, list):
            for item in current:
                if isinstance(item, (dict, list)):
                    stack.append(item)

    return conns, active_conn_sum







def main() -> None:
    # test_connection_history()
    # service = GuacamoleSessionService(sess)
    # pprint.pprint(service.profile_active_connections())

    sess = Startup.get_guacamole_session()

    data = sess.detail_connection(
        '14278',
        'parameters'
    )
    pprint.pprint(data)

    options = {
        'parameters': {},
        'history': {},
        'sharing profiles': {}
    }

    for key, value in options.items():
        print(f'--- {key} ---')
        data = sess.detail_connection(
            '14278',
            key
        )
        pprint.pprint(data)
        input()


if __name__ == '__main__':
    main()
