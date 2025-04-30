from typing import Annotated, Self

from app.common.schemas.base import CustomBaseModel

from fastapi import Request
from pydantic import Field

from user_agents import parse


def get_request_ip(request: Request) -> str:
    '''Resolves the IP address of the client from 
    the request object.

    Args:
        request (Request): _the request_

    Returns:
        str: _the resolved IP address_
    '''
    x_forwarded_for = request.headers.get('X-Forwarded-For')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.client.host  # type: ignore

    return ip


class ClientUserAgent(CustomBaseModel):
    '''Parsed user agent string from the request headers.'''
    user_agent: Annotated[str, Field(
        ...,
        description="The user agent string of the client."
    )]

    device: Annotated[str, Field(
        ...,
        description="The device type of the client."
    )]

    os: Annotated[str, Field(
        ...,
        description="The operating system of the client."
    )]

    browser: Annotated[str, Field(
        ...,
        description="The browser type of the client."
    )]

    is_bot: Annotated[bool, Field(
        ...,
        description="Whether the client is a bot or not."
    )]

    @classmethod
    def create(cls, request: Request) -> Self:
        '''Creates a new instance of the ClientUserAgent class 
        from the request object.

        Args:
            request (Request): _the incoming request_

        Returns:
            Self: _the class instance_
        '''
        user_agent_str = request.headers.get("User-Agent")
        ua_info = parse(user_agent_str)
        return cls(
            user_agent=user_agent_str or 'unknown',
            os=ua_info.get_os(),
            device=ua_info.get_device(),
            browser=ua_info.get_browser(),
            is_bot=ua_info.is_bot
        )

    def __repr__(self) -> str:
        '''Returns a string representation of the class instance.

        Returns:
            str: _the string representation_
        '''
        return f"ClientUserAgent<os={self.os}_device={self.device}_browser={self.browser}_is_bot={self.is_bot})"

    def __eq__(self, other: Self) -> bool:
        '''Compares two instances of the class.

        Args:
            other (Self): _the other instance_

        Returns:
            bool: _whether the two instances are equal_
        '''
        return (
            self.device == other.device and
            self.os == other.os and
            self.browser == other.browser
        )


class ClientFingerprint(CustomBaseModel):
    '''unique finger print of the client'''
    ip_address: Annotated[str, Field(
        ...,
        description="The IP address of the client."
    )]
    user_agent: Annotated[ClientUserAgent, Field(
        ...,
        description="The user agent of the client."
    )]

    @classmethod
    async def create(cls, request: Request) -> Self:
        '''Creates the fingerprint from an incoming request, async to be 
        none blocking.

        Args:
            request (Request): _the client's request_
            user_alias (str | None, optional): _description_. Defaults to None.

        Returns:
            Self: fingerprint instance
        '''
        ip = get_request_ip(request)
        user_agent = ClientUserAgent.create(request)
        return cls(
            ip_address=ip,
            user_agent=user_agent
        )

    def equals(self, other: Self) -> bool:
        '''comapres to fingerprints to see if they are the same.

        Args:
            other (Self): _the other fingerprint_

        Returns:
            bool: _whether or not they match_
        '''
        return (
            self.ip_address == other.ip_address and
            self.user_agent == other.user_agent
        )

    def __eq__(self, other: Self) -> bool:
        return self.equals(other)

    def __repr__(self) -> str:
        return f'Fingerprint<ip={self.ip_address}, {self.user_agent}>'
