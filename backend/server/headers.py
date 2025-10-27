from typing import Annotated, Self

from fastapi import Depends, Request
from pydantic import BaseModel


def get_ip_addr(request: Request, header: str | None) -> str:
    return header.split(',')[0] if header else request.client.host  # type: ignore


class ClientInfo(BaseModel):
    ip_address: str
    user_agent: str

    @classmethod
    def from_request(cls, request: Request) -> Self:
        ip_address = get_ip_addr(request, request.headers.get('x-forwarded-for'))
        user_agent = request.headers.get('user-agent', 'unknown')
        return cls(
            ip_address=ip_address,
            user_agent=user_agent,
        )

    def __str__(self) -> str:
        return f'Client IP {self.ip_address}, User-Agent: {self.user_agent}'


async def get_client_info(request: Request) -> ClientInfo:
    return ClientInfo.from_request(request)


ClientInfoDep = Annotated[ClientInfo, Depends(get_client_info)]
