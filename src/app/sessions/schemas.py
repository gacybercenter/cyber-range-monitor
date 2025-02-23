from pydantic import BaseModel, Field
from fastapi import Request
from typing import Optional
from typing import Annotated
from pydantic import BaseModel, Field, field_validator, StringConstraints
import time

from app.users.models import Role
from .schemas import ClientIdentity
from .constant import SESSION_CONFIG


class SessionData(BaseModel):
    '''A model to represent the dictionary encrypted and stored in the redis
    store that represents a session.
    '''
    username: str = Field(
        ...,
        title="Username",
        description="The username of the users session"
    )
    role: Role = Field(
        ...,
        title="Role",
        description="The role of the user"
    )
    created_at: float = Field(
        ...,
        title="Created At",
        description="The time the session was created in seconds ( time.tme() )"
    )

    client_identity: ClientIdentity = Field(
        ...,
        title="Client Identity",
        description="The metadata of the identity of the user"
    )

    @classmethod
    def create(cls, username: str, role: Role, client_identity: ClientIdentity) -> 'SessionData':
        client_identity.set_mapped_user(username)
        return cls(
            username=username,
            role=role,
            created_at=time.time(),
            client_identity=client_identity
        )

    def exceeds_max_lifetime(self) -> bool:
        return (time.time() - self.created_at) > SESSION_CONFIG.session_lifetime()

    def trusts_client(self, client_identity: ClientIdentity) -> bool:
        return self.client_identity == client_identity

    def __repr__(self) -> str:
        return f"SessionData(username={self.username} role={self.role} created_at={self.created_at})"


class ClientIdentity(BaseModel):
    '''Represents the identity of a client making a request to the server
    used to map a session to an identity of a client to prevent CSRF and 
    session hijacking.    
    '''
    client_ip: str = Field(
        ...,
        description='either the direct or forwarded IP'
    )
    user_agent: str = Field(..., description='the user agent string')
    mapped_user: Optional[str] = Field(
        'Unknown',
        description='a column that can be mapped to a user in the database that identifies client'
    )

    @classmethod
    async def create(cls, request: Request) -> 'ClientIdentity':
        '''Uses the information in the request sent from a client 
        to create an identity

        Arguments:
            request {Request} 

        Returns:
            ClientIdentity -- 
        '''
        ip_addr = request.client.host if request.client else 'n/a'
        if request.headers.get('X-Forwarded-For'):
            forwarded_str = request.headers['X-Forwarded-For']
            ip_addr = forwarded_str.split(',')[0].strip()

        return cls(
            client_ip=ip_addr,
            user_agent=request.headers.get('User-Agent', 'n/a'),
            mapped_user='Unknown'
        )

    def __eq__(self, other: 'ClientIdentity') -> bool:
        return (
            self.client_ip == other.client_ip and
            self.user_agent == other.user_agent
        )

    def set_mapped_user(self, user: str) -> None:
        self.mapped_user = user

    def __repr__(self) -> str:
        return f'ClientIdentity(client_ip={self.client_ip}, user_agent={self.user_agent})'
    