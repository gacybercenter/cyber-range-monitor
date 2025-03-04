import json
from typing import Optional

from app.extensions.security import crypto

from . import client


def session_key(key: str) -> str:
    return f"session:{client.sanitize(key)}"


async def set_session(unsigned_id: str, data: dict, ex: Optional[int] = None) -> None:
    """Store a session in the Redis store

    Arguments:
        key {str} -- the key to store the session under
        data {dict} -- the session data to store

    Keyword Arguments:
        ex {Optional[int]} -- optional expiration time (default: {None})
    """
    session_str = json.dumps(data)
    encrypted_session = crypto.encrypt_data(session_str)
    await client.set_key(session_key(unsigned_id), encrypted_session, ex=ex)


async def get_session(unsigned_id: str) -> Optional[dict]:
    """Get a session from the Redis store

    Arguments:
        key {str} -- the key to get the session from

    Returns:
        Optional[dict] -- the session data if it exists
    """
    encrypted_session = await client.get_key(session_key(unsigned_id))
    if encrypted_session is None:
        return None

    result = None
    try:
        session_str = crypto.decrypt_data(encrypted_session)
        result = json.loads(session_str)
    except Exception:
        pass
    return result


async def delete_session(unsigned_id: str) -> None:
    """Delete a session from the Redis store

    Arguments:
        key {str} -- the key to delete the session from
    """
    safe_key = session_key(unsigned_id)
    await client.delete_key(safe_key)


async def set_session_exp(unsigned_id: str, ex: int) -> None:
    """Set the expiration time for a session

    Arguments:
        key {str} -- the key to set the expiration time for
        ex {int} -- the expiration time in seconds
    """
    await client.set_expiration(session_key(unsigned_id), ex)
