import hashlib
from dataclasses import dataclass

import user_agents
from fastapi import Request


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

    @property
    def id(self) -> str:
        return f'{self.os}.{self.device}.{self.browser}'




@dataclass(slots=True)
class RequestInfo:
    ip: str
    user_agent: UserAgentInfo
    salt: str | None = None

    @property
    def id(self) -> str:
        return f'{self.ip}_{self.user_agent.id}'

    @classmethod
    def create_id(cls, ip: str, user_agent_id: str) -> str:
        """
        Creates a unique identifier for the request based on IP and user agent.

        Parameters
        ----------
        ip : str
            The IP address of the request.
        user_agent_id : str
            The user agent identifier.

        Returns
        -------
        str
            A unique identifier for the request.
        """
        return f'{ip}_{user_agent_id}'

class RequestFingerprinter:

    def get_request_ip(
        self,
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

    def get_user_agent(
        self,
        request: Request
    ) -> UserAgentInfo:
        """
        Extracts the user agent information from the request headers.

        Parameters
        ----------
        request : Request

        Returns
        -------
        UserAgentInfo
            Parsed user agent information.
        """
        user_agent_str = request.headers.get('User-Agent')
        ua_info = user_agents.parse(user_agent_str)
        return UserAgentInfo(
            user_agent=user_agent_str or 'unknown',
            os=ua_info.get_os(),
            device=ua_info.get_device(),
            browser=ua_info.get_browser(),
            is_bot=ua_info.is_bot,
        )

    async def get_fingerprint(
        self,
        request: Request,
        *,
        ip_header: str | None = None,
    ) -> RequestInfo:
        ip = self.get_request_ip(request, request_header=ip_header)
        user_agent = self.get_user_agent(request)
        return RequestInfo(
            ip=ip,
            user_agent=user_agent,
        )

    def hash_request(self, fingerprint: RequestInfo) -> str:
        """
        Hashes the fingerprint using SHA-256.

        Parameters
        ----------
        fingerprint : RequestFingerprint

        Returns
        -------
        str
            The hashed fingerprint.
        """
        encoded = fingerprint.id
        if fingerprint.salt:
            encoded = f'{fingerprint.salt}{encoded}'
        return hashlib.sha256(encoded.encode('utf-8')).hexdigest()

    def check_fingerprint(
        self,
        fingerprint: RequestInfo,
        stored_hash: str
    ) -> bool:
        """
        Checks if the fingerprint matches the given hash.

        Parameters
        ----------
        fingerprint : RequestFingerprint
            The fingerprint to check.
        fingerprint_hash : str
            The hash to compare against.

        Returns
        -------
        bool
            True if the fingerprint matches the hash, False otherwise.
        """
        return self.hash_request(fingerprint) == stored_hash
