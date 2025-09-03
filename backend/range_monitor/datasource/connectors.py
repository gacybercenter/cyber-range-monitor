from __future__ import annotations

import abc
from dataclasses import dataclass
from typing import TYPE_CHECKING, Generic, Self, TypedDict, TypeVar

import guacamole
from openstack import connection

if TYPE_CHECKING:
    from range_monitor.datasource.model import Guacamole, OpenStack

_T = TypeVar('_T')
_C = TypeVar('_C')

class DatasourceConnector(abc.ABC, Generic[_T, _C]):
    '''
    The interface for resolving a database adapter
    into a client which can be used to interface with
    said adapter.
    '''

    @abc.abstractmethod
    @classmethod
    def from_orm(cls, orm: _T, plaintext_password: str) -> Self:
        '''
        Create an DatasourceConnector from a datasource model
        and its decrypted password.

        Parameters
        ----------
        datasource : _T
        plaintext_password : str

        Returns
        -------
        Self
        '''


    @abc.abstractmethod
    def __call__(self) -> _C:
        '''
        Creates a client instance from the specification.

        Returns
        -------
        _C
            _The type of the object used to
            interface with the client_
        '''

@dataclass
class GuacamoleSession(DatasourceConnector['Guacamole', guacamole.session]):
    '''
    Turns a guacamole instance into a callable `guacamole.session` factory.
    '''
    host: str
    data_source: str
    username: str
    password: str

    @classmethod
    def from_orm(
        cls,
        orm: 'Guacamole',
        plaintext_password: str
    ) -> Self:
        return cls(
            host=orm.host,
            data_source=orm.data_source,
            username=orm.username,
            password=plaintext_password
        )

    def __call__(self) -> guacamole.session:
        '''
        Creates a `guacamole.session` object.

        Returns
        -------
        guacamole.session
            _description_

        Raises
        ------
        KeyError
            _The get_token() method fails because the credentials are invalid_
        '''
        return guacamole.session(
            self.host,
            self.data_source,
            self.username,
            self.password
        )

class OpenstackAuthParams(TypedDict):
    """The "auth" dictionary parameter for an openstack connection."""

    endpoint: str
    username: str
    password: str
    user_domain_name: str

    project_id: str | None
    project_name: str | None
    project_domain_name: str | None



@dataclass
class OpenstackConnection(DatasourceConnector['OpenStack', connection.Connection]):
    """
    The specification (or kwargs) for creating an `openstack.connection.Connection`
    object from a `range_monitor.datasource.model.OpenStack` instance.
    """

    auth: OpenstackAuthParams
    region_name: str
    identity_api_version: str

    @classmethod
    def from_orm(
        cls,
        orm: 'OpenStack',
        plaintext_password: str
    ) -> Self:
        auth = OpenstackAuthParams(
            endpoint=orm.auth_url,
            username=orm.username,
            password=plaintext_password,
            user_domain_name=orm.user_domain_name,
            project_id=orm.project_id,
            project_name=orm.project_name,
            project_domain_name=orm.project_domain_name,
        )

        return cls(
            auth=auth,
            region_name=orm.region_name,
            identity_api_version=orm.identity_api_version,
        )

    def __call__(self) -> connection.Connection:
        '''
        Creates an `openstack.connection.Connection` object.

        Returns
        -------
        connection.Connection
            _The openstack connection_
        '''
        return connection.Connection(
            auth=dict(self.auth),
            region_name=self.region_name,
            identity_api_version=self.identity_api_version,
        )

