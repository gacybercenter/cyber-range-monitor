import time
from datetime import datetime
from typing import Annotated, Self

from pydantic import Field

from app.common.schemas.http import CustomBaseModel, RequestSchema, ResponseSchema
from app.common.types import FixedStr
from app.core.security.schema import ClientFingerprint


class LoginBody(RequestSchema):
    """The request body for the login endpoint"""

    username: Annotated[
        FixedStr, Field(..., description="The username of the user to login")
    ]
    password: Annotated[
        FixedStr, Field(..., description="The password of the user to login")
    ]


class SessionIdentity(ResponseSchema):
    """Information about the user assigned an APIKey"""

    username: Annotated[
        str, Field(..., description="The username of the users session")
    ]
    role: Annotated[str, Field(..., description="The role of the user")]


class SessionData(CustomBaseModel):
    """A model to represent the dictionary encrypted and stored in the redis
    store that represents a session.
    """

    identity: Annotated[
        SessionIdentity,
        Field(..., description="the identity of the user associated with the API key"),
    ]

    created_at: Annotated[
        float,
        Field(
            ...,
            description="The time the session was created in seconds ( time.tme() )",
        ),
    ]

    client: Annotated[
        ClientFingerprint,
        Field(..., description="The metadata of the identity of the user"),
    ]

    @classmethod
    def create(cls, username: str, role: str, client: ClientFingerprint) -> "Self":
        """creates a session data object with the given username, role, and client identity
        Returns:
            Self -- the session data object
        """
        return cls(
            identity=SessionIdentity(
                username=username,
                role=role,
            ),
            created_at=time.time(),
            client=client,
        )

    def trusts_client(self, client: ClientFingerprint) -> bool:
        return self.client == client


class SessionResponse(ResponseSchema):
    """The response after a successful login that contains the signed API key and
    the identity of the client
    """

    session_id: Annotated[
        str, Field(..., description="the signed API key to be issued to the client")
    ]
    identity: Annotated[
        SessionIdentity,
        Field(..., description="the identity of the user associated with the API key"),
    ]


class SessionHealth(CustomBaseModel):
    max_age_at: Annotated[
        datetime,
        Field(
            ..., description="the time the session expires in seconds ( time.tme() )"
        ),
    ]
    expires_next: Annotated[
        datetime,
        Field(
            ...,
            description="the time the session expires in seconds ( time.tme() )",
        ),
    ]
    issued_at: Annotated[
        datetime,
        Field(
            ...,
            description="the time the session was created in seconds ( time.tme() )",
        ),
    ]


class SessionInfo(CustomBaseModel):
    """A model to represent the information stored in the redis store"""

    owner: Annotated[
        SessionIdentity | None,
        Field(..., description="the identity of the user associated with the API key"),
    ]
    health: Annotated[
        SessionHealth,
        Field(
            ..., description="the health of the API key with the relevant timestamps"
        ),
    ]


class LogoutResponse(ResponseSchema):
    """A model to represent the response after a successful logout"""

    message: Annotated[
        str,
        Field(
            ...,
            description="the message to be sent to the client after a successful logout",
        ),
    ] = "You have been logged out successfully"
    success: bool = True
