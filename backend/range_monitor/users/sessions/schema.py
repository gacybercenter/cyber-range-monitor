


from typing import Annotated

from pydantic import Field

from range_monitor.core.dates import UTCDate
from range_monitor.schema import ResponseSchema

SessionID = Annotated[
    str,
    Field(
        ...,
        description='The unique identifier of the session.',
    )
]

class SessionClaim(ResponseSchema):
    created_at: UTCDate
    session_id: SessionID
    max_age_at: UTCDate
    idle_timeout_at: UTCDate


class UserSession(ResponseSchema):
    '''
    The admin view of a user session.
    '''
    user_id: str
    created_at: UTCDate
    session_id: SessionID
    user_agent: str | None = Field(
        None,
        description='The user agent of the client that created the session.'
    )
    ip_address: str | None = Field(
        None,
        description='The IP address of the client that created the session.'
    )



class UserSessionList(ResponseSchema):
    sessions: list[UserSession] = Field(
        ...,
        description='A list of active sessions for the user.'
    )
    total: int = Field(..., description='The total number of active sessions.', ge=0)


