from typing import Annotated
from pydantic import BaseModel, Field, field_validator, StringConstraints
import time

from app.core.config import running_config
from app.core.security.models import ClientIdentity
from app.models.user import Role

settings = running_config()





class SessionData(BaseModel):
    '''_summary_
    A model to represent the dictionary encrypted and stored in the redis
    store that represents a session.
    Returns:
        _type_ -- _description_
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
        return (time.time() - self.created_at) > settings.SESSION_MAX_AGE

    def trusts_client(self, client_identity: ClientIdentity) -> bool:
        return self.client_identity == client_identity

    def __repr__(self) -> str:
        return f"SessionData(username={self.username} role={self.role} created_at={self.created_at})"


