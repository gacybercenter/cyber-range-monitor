import secrets
from typing import Optional


from app.extensions.redis.client import get_redis_client
from app.security import crypto

from .schemas import SessionData, ClientIdentity
from .constant import SESSION_CONFIG, SESSION_KEY



class SessionService:
    '''The main service responsible for persistent sessions and the auth flow.

    create(<session_data>):
        The server generates a session id that is digitally signed and salted by the
        server corresponds to a an unsigned key to an encrypted redis dictionary based 
        on "SessionData".

        If the session id isn't used within the SESSION_EXPIRATION_SEC the session is removed from redis 
        and the cookie containing the signed cookie will expire. 

    get_session(<signed_id>):
        The signed id is the cookie stored by the client. 

        The following is checked:
            - The lifetime of the session (session_lifetime()) is greater than the maximum lifetime of the session
            - The session id corresponds to a signature issued by the server that hasn't expired 
            - The session id corresponds to a session in redis
        Once retrieved:
            - The session is extended by another SESSION_EXPIRATION_SEC both in redis
            - The unencrypted "SessionData" is returned  
    '''

    def _create_id(self) -> str:
        return secrets.token_urlsafe(32)

    async def create(self, session_data: SessionData) -> str:
        '''Creates a session id, encrypts session data before storing it in redis and returns
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
        redis = await get_redis_client()

        session_id = self._create_id()
        session_key = f'{SESSION_KEY}{session_id}'
        signed_id = crypto.create_signature(session_id)
        redis.set_encrypted(
            session_key,
            session_data.model_dump(),
            ex=SESSION_CONFIG.session_lifetime()
        )
        return signed_id

    async def get_session(self, signed_id: str, inbound_identity: ClientIdentity) -> Optional[SessionData]:
        '''Provided a signed session id from the cookie stored by the client, 
        returns the unencrypted session data. 

        The following is checked:
            - The lifetime of the session (session_lifetime()) is greater than the maximum lifetime of the session
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
            session_id = crypto.load_signature(
                signed_id,
                max_age=SESSION_CONFIG.session_lifetime()
            )
        except Exception:
            return None

        redis = await get_redis_client()
        session_key = f'{SESSION_KEY}{session_id}'
        data_dump: Optional[dict] = redis.get_decrypted(session_key)
        if not data_dump:
            return None

        session_meta = SessionData(**data_dump)
        
        if not self.session_valid(inbound_identity, session_meta):
            redis.remove(session_key)
            return None 
        
        return session_meta

    def session_valid(self, inbound_client, session_data: SessionData) -> bool:
        session_expired = session_data.exceeds_max_lifetime()
        untrusted_client = not session_data.trusts_client(inbound_client)
        return session_expired or untrusted_client
        
    
    async def end_session(self, signed_id: str) -> None:
        try:
            session_id = crypto.load_signature(
                signed_id,
                max_age=SESSION_CONFIG.session_lifetime()
            )
        except Exception:
            return

        redis = await get_redis_client()
        session_key = f'{SESSION_KEY}{session_id}'
        redis.remove(session_key)


async def get_session_service() -> SessionService:
    return SessionService()