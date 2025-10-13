# api response schemas from guacamole
import time

from pydantic import ConfigDict, Field

from range_monitor.core.schema import AliasGenerator, PydanticMixin


class GuacamoleModel(PydanticMixin):
    model_config = ConfigDict(
        alias_generator=AliasGenerator.to_camel_case,
        populate_by_name=True,
    )

class AttributeModel(PydanticMixin):
    model_config = ConfigDict(
        alias_generator=AliasGenerator.kebab_case,
        populate_by_name=True,
    )


class ConnectionAttributes(AttributeModel):
    """
    Represents the attributes of a connection in
    Guacamole, there are more but these are the consistent
    ones that are worth modeling.
    """
    max_connections: int | None = None
    max_connections_per_user: int | None = None
    weight: int | None = None
    failover_only: bool | None = None
    guacd_hostname: str | None = None
    guacd_port: int | None = None


class ConnectionInstance(GuacamoleModel):
    '''
    from list_active_connections()
    '''
    connectable: bool
    connection_identifier: str
    identifier: str
    start_date: int
    username: str
    remote_host: str

class Connection(GuacamoleModel):
    '''
    from list_connections()

    '''
    identifier: str
    active_connections: int
    name: str
    protocol: str
    last_active: int | None = None
    attributes: ConnectionAttributes


class GroupAttributes(AttributeModel):
    max_connections: int | None = None
    max_connections_per_user: int | None = None
    enable_session_affinity: bool | None = None

class ConnectionGroup(GuacamoleModel):
    '''
    from list_connection_groups()
    '''
    identifier: str
    name: str
    group_type: str = Field(
        alias='type'
    )
    attributes: GroupAttributes
    parent_identifier: str | None = None
    active_connections: int

class UserAttributes(AttributeModel):

    guac_email_address: str | None = None
    guac_full_name: str | None = None
    guac_organization: str | None = None
    guac_organization_role: str | None = None

class GuacUser(GuacamoleModel):
    '''
    single entry of list_users() and get_user()
    '''
    attributes: UserAttributes
    last_active: int | None = None
    username: str


class HistoryEntry(GuacamoleModel):
    '''
    from get_user_history() and get_connection_history()
    '''
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

    def end_time(self) -> int:
        if self.end_date is None:
            return round(time.time() * 1000)
        return self.end_date

    @property
    def elapsed(self) -> int:
        '''
        Returns the elapsed time in milliseconds.
        '''
        return self.end_time() - self.start_date



