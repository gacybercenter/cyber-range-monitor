import ipaddress
from dataclasses import dataclass

import user_agents
from fastapi import Request


@dataclass(slots=True, frozen=True)
class IpInfo:
    """
    Utility class for storing and manipulating client IP addresses.
    """

    ip_address: str

    def get_network_prefix(
        self,
        ip_address: str,
        *,
        v4_prefix: int = 24,
        v6_prefix: int = 64,
    ) -> str:
        network_addr = self.ip_address

        try:
            addr = ipaddress.ip_address(ip_address)

            prefix = v4_prefix if addr.version == 4 else v6_prefix
            network = ipaddress.ip_network(f'{ip_address}/{prefix}', strict=False)
            network_addr = str(network.network_address)
        except Exception:
            pass

        return network_addr


def get_request_ip(
    request: Request,
    *,
    request_header: str | None,
) -> str:
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
    hdr = request_header or 'X-Forwarded-For'

    x_forwarded_for = request.headers.get(hdr)
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.client.host  # type: ignore

    return ip


@dataclass(slots=True, frozen=True)
class UserAgentInfo:
    """Parsed user agent string from the request headers."""

    user_agent: str
    device: str
    os: str
    browser: str
    is_bot: bool

    def __repr__(self) -> str:
        return (
            f'UserAgentInfo<os={self.os}_device={self.device}'
            f'browser={self.browser}_is_bot={self.is_bot}>'
        )

    def identifier(self) -> str:
        return f'{self.os}.{self.device}.{self.browser}'


async def parse_user_agent(request: Request) -> UserAgentInfo:
    user_agent_str = request.headers.get('User-Agent')
    ua_info = user_agents.parse(user_agent_str)
    return UserAgentInfo(
        user_agent=user_agent_str or 'unknown',
        os=ua_info.get_os(),
        device=ua_info.get_device(),
        browser=ua_info.get_browser(),
        is_bot=ua_info.is_bot,
    )


async def parse_request_ip(
    request: Request,
    *,
    request_header: str | None = None,
) -> IpInfo:
    ip_address = get_request_ip(request, request_header=request_header)
    return IpInfo(ip_address=ip_address)


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
