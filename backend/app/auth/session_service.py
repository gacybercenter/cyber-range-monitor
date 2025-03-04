import secrets
import time

from fastapi import Request, Response

from app import config
from app.extensions.redis import session_store
from app.extensions.security import crypto

from .schemas import ClientIdentity, SessionData

session_config = config.get_config_yml().session

COOKIE_NAME = "session_id"  # can't put in const bc of circular imports


def create_session_id() -> str:
    """Generates a session id that is used to store a session in redis"""
    return secrets.token_urlsafe(32)


def session_lifetime_reached(session_data: SessionData) -> bool:
    """Checks if the session has reached the maximum lifetime"""
    session_lifetime = time.time() - session_data.created_at
    return session_lifetime > session_config.session_max_lifetime()


async def store_session(session_data: SessionData) -> str:
    """Creates a session id, encrypts session data before storing it in redis and returns
    a signed session id to be issued to the client.

    The server generates a session id that is digitally signed and salted by the
    server corresponds to a an unsigned key to an encrypted redis dictionary based
    on "SessionData".

    If the session id isn't used within the SESSION_EXPIRATION_SEC the session is removed from redis
    and the cookie containing the signed cookie will expire.

    Arguments:
        session_data {SessionData} -- The data to be stored in the session

    Returns:
        str -- The signed session id to be issued to the client
    """
    session_id = create_session_id()
    signed_id = crypto.create_signature(session_id)
    await session_store.set_session(
        session_id, session_data.model_dump(), ex=session_config.session_max_lifetime()
    )
    return signed_id


async def create_session_cookie(
    username: str, role: str, client_identity: ClientIdentity
) -> dict:
    """Creates session data from the authenticated user, stores it in the
    Redis Store and returns the kwargs to set a cookie in the response
    """
    client_identity.set_mapped_user(username)
    session_data = SessionData.create(
        username=username, role=role, client_identity=client_identity
    )
    signed_id = await store_session(session_data)
    return session_config.cookie_kwargs(signed_id)


async def revoke_session(signed_id: str | None, response: Response) -> None:
    if signed_id:
        await end_session(signed_id)
    response.delete_cookie(COOKIE_NAME)


async def get_session_cookie(request: Request) -> str | None:
    """Gets the session cookie from the request"""
    return request.cookies.get(COOKIE_NAME)


async def get_session(
    signed_id: str, inbound_client: ClientIdentity
) -> SessionData | None:
    """gets the session provided the signed_id from the client cookies and checks
    if the max lifetime is reached, was issued by the server and exists in the
    redis session store. returns none if the session is invalid or expired

    Arguments:
        signed_id {str} -- the signed id in client cookies
        inbound_client {ClientIdentity} -- the inbound identity of the client

    Returns:
        Optional[SessionData]
    """

    try:
        session_id = crypto.load_signature(
            signed_id, max_age=session_config.session_max_lifetime()
        )
    except Exception:
        return None

    session_dump = await session_store.get_session(session_id)
    if not session_dump:
        return None

    try:
        session_data = SessionData(**session_dump)
    except Exception:
        return None

    session_highjacked = not session_data.trusts_client(inbound_client)
    if session_lifetime_reached(session_data) or session_highjacked:
        await session_store.delete_session(session_id)
        return None

    return session_data


async def end_session(signed_id: str) -> None:
    """Loads the signed session ID, removes it from the redis store

    Arguments:
        signed_id {str} -- the signed id in client cookies
    """
    try:
        session_id = crypto.load_signature(
            signed_id, max_age=session_config.session_max_lifetime()
        )
    except Exception:
        return
    await session_store.delete_session(session_id)
