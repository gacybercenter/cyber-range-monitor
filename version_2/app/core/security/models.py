from typing import Optional
from fastapi import Request
from pydantic import BaseModel, Field




class ClientIdentity(BaseModel):
    '''Represents the identity of a client making a request to the server
    used to map a session to an identity of a client to prevent CSRF and 
    session hijacking.    
    '''
    client_ip: str = Field(
        ...,
        description='either the direct or forwarded IP'
    )
    user_agent: str = Field(..., description='the user agent string')
    mapped_user: Optional[str] = Field(
        'Unknown',
        description='a column that can be mapped to a user in the database that identifies client'
    )

    @classmethod
    async def create(cls, request: Request) -> 'ClientIdentity':
        '''Uses the information in the request sent from a client 
        to create an identity

        Arguments:
            request {Request} 

        Returns:
            ClientIdentity -- 
        '''
        ip_addr = request.client.host if request.client else 'n/a'
        if request.headers.get('X-Forwarded-For'):
            forwarded_str = request.headers['X-Forwarded-For']
            ip_addr = forwarded_str.split(',')[0].strip()

        return cls(
            client_ip=ip_addr,
            user_agent=request.headers.get('User-Agent', 'n/a'),
            mapped_user='Unknown'
        )

    def __eq__(self, other: 'ClientIdentity') -> bool:
        return (
            self.client_ip == other.client_ip and
            self.user_agent == other.user_agent
        )

    def set_mapped_user(self, user: str) -> None:
        self.mapped_user = user

    def __repr__(self) -> str:
        return f'ClientIdentity(client_ip={self.client_ip}, user_agent={self.user_agent})'


