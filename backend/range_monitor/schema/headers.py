from typing import Annotated, Self

import user_agents
from fastapi import Depends, Header, Request
from pydantic import BaseModel


class UserAgent(BaseModel):
    browser: str
    os: str
    device: str
    is_bot: bool
    raw_header: str


    @classmethod
    def from_header(cls, header: str) -> 'UserAgent':
        ua = user_agents.parse(header)
        return cls(
            browser=f'{ua.browser.family} {ua.browser.version_string}',
            os=f'{ua.os.family} {ua.os.version_string}',
            device=f'{ua.device.family} {ua.device.brand} {ua.device.model}',
            is_bot=ua.is_bot,
            raw_header=header,
        )

    def __str__(self) -> str:
        return (
            f'{self.browser} on {self.os}, Device: {self.device}, '
            f'Is Bot: {self.is_bot}'
        )


RequestID = Annotated[str, Header(
    alias='X-Request-ID',
    description='A unique identifier for the request, used for tracing and correlation',
)]

UserAgentHeader = Annotated[str, Header(
    alias='User-Agent',
    description='The User-Agent string of the client making the request',
)]

IPHeader = Annotated[str, Header(
    alias='X-Forwarded-For',
    description=(
        'The originating IP address of the client making the request, '
        'if behind a proxy or load balancer'
    ),
)]


def parse_request_ip(request: Request, header: str | None) -> str:
    """
    Extracts the client's IP address from the request.

    Parameters
    ----------
    request : Request
    request_header : str | None, optional
        _if none uses X-Forwarded-For_, by default None

    Returns
    -------
    str
    """

    if header:
        ip = header.split(',')[0]
    else:
        ip = request.client.host  # type: ignore

    return ip


class Device(BaseModel):
    ip_address: str
    user_agent: UserAgent

    @classmethod
    def from_request(cls, request: Request) -> Self:
        ip_address = parse_request_ip(
            request,
            request.headers.get('X-Forwarded-For')
        )
        user_agent = UserAgent.from_header(
            request.headers.get('User-Agent', 'unknown')
        )
        return cls(ip_address=ip_address, user_agent=user_agent)

    def __str__(self) -> str:
        return f'Client IP {self.ip_address}, User-Agent: {self.user_agent}'


async def get_client_device(
    request: Request,
    user_agent: UserAgentHeader,
    ip_address: IPHeader
) -> Device:
    """
    Dependency to extract client device information from the request.

    Parameters
    ----------
    request : Request
    user_agent : str
        The User-Agent header from the request.
    ip_address : str
        The X-Forwarded-For header from the request.

    Returns
    -------
    Device
        An instance of the Device model containing IP and User-Agent info.
    """
    ip = parse_request_ip(request, ip_address)
    ua = UserAgent.from_header(user_agent)
    return Device(ip_address=ip, user_agent=ua)


DeviceDep = Annotated[Device, Depends(get_client_device)]