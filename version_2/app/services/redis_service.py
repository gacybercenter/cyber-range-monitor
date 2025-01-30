from aioredis import Redis
from app.core import settings
import uuid
from app.schemas.auth_schemas import AccessTokenPayload





class RedisClient:
    _client: Redis = None  # type: ignore
    _instance = None

    @classmethod
    def get_instance(cls) -> 'RedisClient':
        if cls._instance is None:
            cls._instance = cls()
            cls._client = Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                decode_responses=True
            )
        return cls._instance

    @classmethod
    async def create_session(cls, username: str) -> str:
        session_id = str(uuid.uuid4())
        await cls._client.setex(
            f'refresh:{session_id}',
            settings.JWT_REFRESH_EXP_SEC,
            username
        )
        return session_id

    @classmethod 
    async def set_access_token(cls, username: str, access_token: str) -> None:
        await cls._client.setex(
            f'access_token:{username}',
            settings.JWT_ACCESS_EXP_MIN,
            access_token
        )
    
    @classmethod 
    async def delete_access_token(cls, username: str) -> None:
        key = f'access_token:{username}'
        if await cls._client.exists(key):
            await cls._client.delete(key)
    
    @classmethod
    async def get_session(cls, session_id: str) -> str:
        return await cls._client.get(f'refresh:{session_id}')

    @classmethod
    async def delete_session(cls, session_id: str) -> None:
        search = f'refresh:{session_id}'
        if await cls._client.exists(search):
            await cls._client.delete(search)
    
    
    
        '''
            create a session id for refreshing the session 
            until redis automatically expires it 
            
            have a  
            'username:access_token' -> encoded_token 
            
            then when the clients token expires 
            
            get the session id which returns the username
            
            user the 
            'access_token:username'
            to get the current users access token and then 
            overwrite it be re setting it 
        '''
    
            
    
    
    
     
    
    
    

