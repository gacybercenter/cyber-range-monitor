
from typing import Annotated, Self

from pydantic import ConfigDict, Field

from range_monitor.core.pydantic import AliasGenerator, PydanticMixin


class GuacamoleDTO(PydanticMixin):
    model_config = ConfigDict(
        alias_generator=AliasGenerator.to_camel_case,
        populate_by_name=True,
    )


class GuacamoleAttributeDTO(PydanticMixin):
    model_config = ConfigDict(
        alias_generator=AliasGenerator.kebab_case,
        populate_by_name=True,
    )

InstanceID = Annotated[
    str,
    Field(
        description=(
            'The identifier for the ongoing session '
            'to the connection which is created at the '
            'time the user connects. The actual identifier of '
            'the connection is in connection_identifier'
        ),
    )
]

ConnectionIdentifier = Annotated[
    str,
    Field(
        description=(
            'So this kinda tripped me up and I ll explain this so you dont have to '
            'find out for yourself. The "identifier" field in the Guacamole '
            'API response is actually the connection_identifier, which is the '
            'unique ID for a connection which a user can connect to. And this is '
            'the connection_identifier field in the ActiveGuacamoleConnection '
        )
    ),
]

class ActiveGuacamoleConnection(GuacamoleDTO):
    """
    Represents a single active connection in Guacamole
    returned from list_active_connections()

    Parameters
    ----------
    GuacamoleDTO
    """

    connectable: bool
    connection_id: ConnectionIdentifier
    instance_id: InstanceID
    start_date: int
    username: str
    remote_host: str

    @classmethod
    def convert(cls, data: dict) -> Self:
        connection_id = data.pop('connectionIdentifier')
        instance_id = data.pop('identifier')
        return cls(
            connection_id=connection_id,
            instance_id=instance_id,
            **data,
        )


class ConnectionAttributes(GuacamoleAttributeDTO):
    """
    Represents the attributes of a connection group in
    Guacamole, there are more but these are the consistent
    ones that are worth modeling.
    """

    max_connections: int | None = None
    max_connections_per_user: int | None = None
    weight: int | None = None
    failover_only: bool | None = None
    guacd_hostname: str | None = None
    guacd_port: int | None = None


class Connection(GuacamoleDTO):
    """
    Represents a connection in Guacamole,
    it's returned from multiple api calls.
    """

    identifier: ConnectionIdentifier
    active_connections: int
    name: str
    parent_identifier: str | None = None
    protocol: str
    last_active: int | None = None
    attributes: ConnectionAttributes

class ConnectionInstance(GuacamoleDTO):
    instance_id: InstanceID
    start_date: int
    username: str
    remote_host: str




class ConnectionGroupAttributes(GuacamoleAttributeDTO):
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


class ActiveConnectionProfile(GuacamoleDTO):
    identifier: str
    connection_name: str
    username: str

class UserDetailAttributes(GuacamoleAttributeDTO):
    """
    From detail_user()
    """

    guac_email_address: str | None = None
    guac_full_name: str | None = None
    guac_organization: str | None = None
    guac_organization_role: str | None = None


class GuacamoleUser(GuacamoleDTO):
    """
    From detail_user()
    """

    attributes: UserDetailAttributes
    last_active: int | None = None
    username: str

class ConnectionInstanceInfo(GuacamoleDTO):
    organization: str
    connection: ConnectionInstance
    user: GuacamoleUser

class GuacamoleUserActivity(GuacamoleDTO):
    usernames: list[str] = Field(
        default_factory=list,
        description='List of unique usernames with active connections',
    )
    organization_activity: dict[str, list[ConnectionInstanceInfo]] = Field(
        default_factory=dict,
        description='Mapping of organizations to their list of active users',
    )

    def register(
        self,
        *,
        user: GuacamoleUser,
        connection: ConnectionInstance
    ) -> None:
        organization = user.attributes.guac_organization or 'Unassigned'
        self.organization_activity.setdefault(organization, []).append(
            ConnectionInstanceInfo(
                organization=organization,
                connection=connection,
                user=user
            )
        )