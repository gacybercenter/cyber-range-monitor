from typing import TYPE_CHECKING, TypedDict

from range_monitor.core.pydantic import PydanticMixin
from range_monitor.datasource.specs import ConnectionSpec

if TYPE_CHECKING:
    from typing import Self

    from range_monitor.datasource.model import OpenStack

class OpenstackAuthParams(TypedDict):
    """The "auth" dictionary parameter for an openstack connection."""

    endpoint: str
    username: str
    password: str
    user_domain_name: str

    project_id: str | None
    project_name: str | None
    project_domain_name: str | None


class OpenStackConnectionSpec(PydanticMixin, ConnectionSpec['OpenStack']):
    '''
    The specification (or kwargs) for creating an `openstack.connection.Connection`
    object from a `range_monitor.datasource.model.OpenStack` instance.
    '''
    auth: OpenstackAuthParams
    region_name: str
    identity_api_version: str

    @classmethod
    def create_from_source(
        cls,
        datasource: 'OpenStack',
        plaintext_password: str
    ) -> Self:
        auth = OpenstackAuthParams(
            endpoint=datasource.auth_url,
            username=datasource.username,
            password=plaintext_password,
            user_domain_name=datasource.user_domain_name,
            project_id=datasource.project_id,
            project_name=datasource.project_name,
            project_domain_name=datasource.project_domain_name,
        )
        return cls(
            auth=auth,
            region_name=datasource.region_name,
            identity_api_version=datasource.identity_api_version,
        )