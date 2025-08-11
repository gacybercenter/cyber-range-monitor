from dataclasses import dataclass
from typing import Self

from fastapi import Request
from user_agents import parse


def get_request_ip(request: Request) -> str:
    """Resolves the IP address of the client from
    the request object.

    Args:
        request (Request): _the request_

    Returns:
        str: _the resolved IP address_
    """
    x_forwarded_for = request.headers.get("X-Forwarded-For")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
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


    @classmethod
    def parse_request(cls, request: Request) -> Self:
        user_agent_str = request.headers.get("User-Agent")
        ua_info = parse(user_agent_str)
        return cls(
            user_agent=user_agent_str or "unknown",
            os=ua_info.get_os(),
            device=ua_info.get_device(),
            browser=ua_info.get_browser(),
            is_bot=ua_info.is_bot,
        )

    def __repr__(self) -> str:
        return f"UserAgentInfo<os={self.os}_device={self.device}_browser={self.browser}_is_bot={self.is_bot})"

    def __eq__(self, other: Self) -> bool:
        return (
            self.device == other.device
            and self.os == other.os
            and self.browser == other.browser
        )

@dataclass(slots=True, frozen=True)
class ClientFingerprint:
    """unique finger print of the client"""

    ip_address: str
    user_agent: UserAgentInfo

    @classmethod
    async def from_request(cls, request: Request) -> Self:
        ip = get_request_ip(request)
        user_agent = UserAgentInfo.parse_request(request)
        return cls(ip_address=ip, user_agent=user_agent)

    def equals(self, other: Self) -> bool:
        """comapres to fingerprints to see if they are the same.

        Args:
            other (Self): _the other fingerprint_

        Returns:
            bool: _whether or not they match_
        """
        return (
            self.ip_address == other.ip_address and self.user_agent == other.user_agent
        )

    def __eq__(self, other: Self) -> bool:
        return self.equals(other)

async def get_client_fingerprint(request: Request) -> ClientFingerprint:
    return await ClientFingerprint.from_request(request)