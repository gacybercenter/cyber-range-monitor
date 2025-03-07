import json

from app.extensions.security import crypto

from app.extensions import redis_client


def api_key_prefix(key: str) -> str:
    return f"api_key:{redis_client.sanitize(key)}"


async def set_api_key(unsigned_id: str, data: dict, ex: int | None = None) -> None:
    """Store a session in the Redis store

    Arguments:
        key {str} -- the key to store the session under
        data {dict} -- the session data to store

    Keyword Arguments:
        ex {Optional[int]} -- optional expiration time (default: {None})
    """
    session_str = json.dumps(data)
    encrypted_session = crypto.encrypt_data(session_str)
    print('key set:', api_key_prefix(unsigned_id))
    await redis_client.set_key(api_key_prefix(unsigned_id), encrypted_session, ex=ex)


async def get_api_key(unsigned_id: str) -> dict | None:
    """Get a session from the Redis store

    Arguments:
        key {str} -- the key to get the session from

    Returns:
        Optional[dict] -- the session data if it exists
    """
    print('\n\n\nkey get:', api_key_prefix(unsigned_id))
    encrypted_session = await redis_client.get_key(api_key_prefix(unsigned_id))
    if encrypted_session is None:
        return None

    result = None
    try:
        session_str = crypto.decrypt_data(encrypted_session)
        result = json.loads(session_str)
    except Exception:
        pass
    return result


async def delete_api_key(unsigned_id: str) -> None:
    """Delete a session from the Redis store

    Arguments:
        key {str} -- the key to delete the session from
    """
    safe_key = api_key_prefix(unsigned_id)
    await redis_client.delete_key(safe_key)


async def set_key_exp(unsigned_id: str, ex: int) -> None:
    """Set the expiration time for a session

    Arguments:
        key {str} -- the key to set the expiration time for
        ex {int} -- the expiration time in seconds
    """
    await redis_client.set_expiration(api_key_prefix(unsigned_id), ex)
