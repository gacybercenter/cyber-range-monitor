import secrets
from typing import Optional
from app.services.security.redis_client import RedisClient
from app.core.security import crypto_utils
from app.core.config import running_config
from app.schemas.session_schema import SessionData

settings = running_config()
SESSION_KEY = 'session:'


class SessionIdentity:
    '''_summary_
    The main service responsible for persistent sessions and the auth flow.

    create(<session_data>):
        The server generates a session id that is digitally signed and salted by the
        server corresponds to a an unsigned key to an encrypted redis dictionary based 
        on "SessionData".

        If the session id isn't used within the SESSION_EXPIRATION_SEC the session is removed from redis 
        and the cookie containing the signed cookie will expire. 

    get_session(<signed_id>):
        The signed id is the cookie stored by the client. 

        The following is checked:
            - The lifetime of the session (SESSION_MAX_AGE) is greater than the maximum lifetime of the session
            - The session id corresponds to a signature issued by the server that hasn't expired 
            - The session id corresponds to a session in redis
        Once retrieved:
            - The session is extended by another SESSION_EXPIRATION_SEC both in redis
            - The unencrypted "SessionData" is returned  
    '''
    
    def _create_id(self) -> str:
        return secrets.token_urlsafe(32)

    def create(self, session_data: SessionData) -> str:
        '''_summary_
        Creates a session id, encrypts session data before storing it in redis and returns
        a signed session id to be issued to the client.

        The server generates a session id that is digitally signed and salted by the
        server corresponds to a an unsigned key to an encrypted redis dictionary based 
        on "SessionData".

        If the session id isn't used within the SESSION_EXPIRATION_SEC the session is removed from redis 
        and the cookie containing the signed cookie will expire.

        Arguments:
            session_data {SessionData} -- _description_

        Returns:
            str -- _description_
        '''
        redis = RedisClient.get_instance()

        session_id = self._create_id()
        session_key = f'{SESSION_KEY}{session_id}'
        signed_id = crypto_utils.create_signature(session_id)
        redis.set_encrypted(
            session_key,
            session_data.model_dump(),
            ex=settings.SESSION_EXPIRATION_SEC
        )
        return signed_id

    def get_session(self, signed_id: str) -> Optional[SessionData]:
        '''_summary_
        Provided a signed session id from the cookie stored by the client, 
        returns the unencrypted session data. 

        The following is checked:
            - The lifetime of the session (SESSION_MAX_AGE) is greater than the maximum lifetime of the session
            - The session id corresponds to a signature issued by the server that hasn't expired 
            - The session id corresponds to a session in redis
        Once retrieved:
            - The session is extended by another SESSION_EXPIRATION_SEC both in redis
            - The unencrypted "SessionData" is returned  
        Arguments:
            signed_id {str} -- _description_

        Returns:
            Optional[SessionData] -- _description_
        '''
        try:
            session_id = crypto_utils.load_signature(
                signed_id,
                max_age=settings.SESSION_MAX_AGE
            )
        except Exception:
            return None

        redis = RedisClient.get_instance()
        session_key = f'{SESSION_KEY}{session_id}'
        data_dump: Optional[dict] = redis.get_decrypted(session_key)
        if not data_dump:
            return None

        try:
            session_meta = SessionData(**data_dump)
            if session_meta.exceeds_max_lifetime():
                redis.remove(session_key)
                return None
        except Exception:
            return None

        redis.set_key_expiration(
            session_key,
            settings.SESSION_EXPIRATION_SEC
        )

        return session_meta

    def end_session(self, signed_id: str) -> None:
        try:
            session_id = crypto_utils.load_signature(
                signed_id,
                max_age=settings.SESSION_EXPIRATION_SEC
            )
        except Exception:
            return None

        redis = RedisClient.get_instance()
        session_key = f'{SESSION_KEY}{session_id}'
        redis.remove(session_key)
