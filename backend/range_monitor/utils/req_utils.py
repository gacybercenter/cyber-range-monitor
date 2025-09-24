from dataclasses import dataclass
from typing import Annotated

import user_agents
from fastapi import Header, Request


@dataclass(slots=True)
class UserAgent:
    browser: str
    os: str
    device: str
    is_bot: bool
    raw_header: str | None

    def __repr__(self) -> str:
        return (
            f'UserAgent(browser={self.browser}, os={self.os}, '
            f'device={self.device}, is_bot={self.is_bot})'
        )



def get_request_path(request: Request) -> str:
    """
    Extracts the path from the request URL.

    Parameters
    ----------
    request : Request

    Returns
    -------
    str
        The path of the request URL.
    """
    return (
        request.url.path
        if not request.url.query
        else request.url.path + '/' + request.url.query
    )

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

def parse_user_agent(request: Request, header: str | None) -> UserAgent | None:
    """
    Collects and parses the User-Agent header from the request.

    Parameters
    ----------
    request : Request

    Returns
    -------
    UserAgent
    """
    if header is None and not (header := request.headers.get('User-Agent')):
        return None

    ua = user_agents.parse(header)
    return UserAgent(
        browser=f'{ua.browser.family} {ua.browser.version_string}',
        os=f'{ua.os.family} {ua.os.version_string}',
        device=f'{ua.device.family} {ua.device.brand} {ua.device.model}',
        is_bot=ua.is_bot,
        raw_header=header,
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
    default=None,
    description=(
        'The originating IP address of the client making the request, '
        'if behind a proxy or load balancer'
    ),
)]


async def get_user_agent(
    request: Request,
    user_agent: UserAgentHeader | None = None
) -> UserAgent | None:
    return parse_user_agent(request, user_agent)

async def get_request_id(request_id: RequestID | None = None) -> str:
    return request_id or 'n/a'

async def get_request_ip(
    request: Request,
    request_ip: IPHeader | None = None
) -> str | None:
    return parse_request_ip(request, request_ip)