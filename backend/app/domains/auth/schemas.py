from datetime import datetime
import time
from typing import Annotated, Optional

from fastapi import Request
from pydantic import Field

from app.core.schemas import CustomBaseModel


class KeyBearerIdentity(CustomBaseModel):
    '''Information about the user assigned an APIKey'''
    username: Annotated[str, Field(
        ...,
        description="The username of the users session"
    )]
    role: Annotated[str, Field(...,  description="The role of the user")]


class ClientIdentity(CustomBaseModel):
    """Represents the identity of a client making a request to the server
    used to map a session to an identity of a client to prevent CSRF and
    session hijacking.
    """

    client_ip: Annotated[str, Field(
        ...,
        description="either the direct or forwarded IP"
    )]
    user_agent: Annotated[str, Field(..., description="the user agent string")]

    @classmethod
    async def create(cls, request: Request) -> "ClientIdentity":
        """Uses the information in the request sent from a client
        to create an identity

        Arguments:
            request {Request}

        Returns:
            ClientIdentity 
        """
        ip_addr = request.client.host if request.client else "n/a"
        if request.headers.get("X-Forwarded-For"):
            forwarded_str = request.headers["X-Forwarded-For"]
            ip_addr = forwarded_str.split(",")[0].strip()

        return cls(
            client_ip=ip_addr,
            user_agent=request.headers.get("User-Agent", "n/a")
        )

    def __eq__(self, other: "ClientIdentity") -> bool:  # type: ignore
        return self.client_ip == other.client_ip and self.user_agent == other.user_agent

    def __repr__(self) -> str:
        return (
            f"ClientIdentity(client_ip={self.client_ip}, user_agent={self.user_agent})"
        )


class APIKeyData(CustomBaseModel):
    """A model to represent the dictionary encrypted and stored in the redis
    store that represents a session.
    """

    identity: Annotated[KeyBearerIdentity, Field(
        ..., description="the identity of the user associated with the API key"
    )]

    created_at: Annotated[float, Field(
        ...,
        description="The time the session was created in seconds ( time.tme() )",
    )]

    client_identity: Annotated[ClientIdentity, Field(
        ...,
        description="The metadata of the identity of the user",
    )]

    @classmethod
    def create(
        cls, username: str, role: str, client_identity: ClientIdentity
    ) -> "APIKeyData":
        """creates a session data object with the given username, role, and client identity
        Returns:
            APIKeyPayload -- the session data object
        """
        return cls(
            identity=KeyBearerIdentity(
                username=username,
                role=role,
            ),
            created_at=time.time(),
            client_identity=client_identity,
        )

    def trusts_client(self, client_identity: ClientIdentity) -> bool:
        return self.client_identity == client_identity


class APIKeyResponse(CustomBaseModel):
    '''The response after a successful login that contains the signed API key and
    the identity of the client 
    '''
    api_key: Annotated[str, Field(
        ...,
        description="the signed API key to be issued to the client"
    )]
    identity: Annotated[KeyBearerIdentity, Field(
        ...,
        description="the identity of the user associated with the API key"
    )]


class APIKeyHealth(CustomBaseModel):
    max_age_at: Annotated[datetime, Field(
        ...,
        description="the time the session expires in seconds ( time.tme() )"
    )]
    expires_next: Annotated[datetime, Field(
        ...,
        description="the time the session expires in seconds ( time.tme() )",
    )]
    issued_at: Annotated[datetime, Field(
        ...,
        description="the time the session was created in seconds ( time.tme() )",
    )]


class KeyInfo(CustomBaseModel):
    '''A model to represent the information stored in the redis store'''
    owner: Annotated[Optional[KeyBearerIdentity], Field(
        ...,
        description="the identity of the user associated with the API key"
    )]
    health: Annotated[APIKeyHealth, Field(
        ...,
        description="the health of the API key with the relevant timestamps"
    )]


class LogoutResponse(CustomBaseModel):
    '''A model to represent the response after a successful logout'''
    message: Annotated[str, Field(
        ...,
        description="the message to be sent to the client after a successful logout"
    )] = "You have been logged out successfully"
    success: bool = True
