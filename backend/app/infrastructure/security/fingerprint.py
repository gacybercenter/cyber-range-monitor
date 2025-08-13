import hashlib
from typing import Self

from fastapi import Request

from app.core.pydantic import CustomBaseModel
from app.utils.request_parse import (
    IpInfo,
    UserAgentInfo,
    get_request_path,
    parse_request_ip,
    parse_user_agent,
)


class RequestFingerprint(CustomBaseModel):
    ip: IpInfo
    user_agent: UserAgentInfo
    salt: str | None = None
    request_path: str | None = None

    @property
    def id(self) -> str:
        return f'{self.ip.ip_address}.{self.user_agent.identifier()}'

    @classmethod
    async def parse_request(
        cls,
        request: Request,
        *,
        ip_header: str | None = None,
    ) -> Self:
        """
        Parses the request to extract the fingerprint information.

        Parameters
        ----------
        request : Request
            The FastAPI request object.
        """
        ip = await parse_request_ip(request, request_header=ip_header)
        user_agent = await parse_user_agent(request)
        request_path = get_request_path(request)
        return cls(
            ip=ip,
            user_agent=user_agent,
            request_path=request_path,
        )


def hash_fingerprint(
    fingerprint: RequestFingerprint, *, salt: str | None = None
) -> str:
    encoded = fingerprint.id
    if salt:
        encoded = f'{salt}{encoded}'
    return hashlib.sha256(encoded.encode('utf-8')).hexdigest()


def check_fingerprint(
    fingerprint: RequestFingerprint, fingerprint_hash: str, *, salt: str | None = None
) -> bool:
    """
    Checks if the fingerprint matches the given hash.

    Parameters
    ----------
    fingerprint : RequestFingerprint
        The fingerprint to check.
    fingerprint_hash : str
        The hash to compare against.
    salt : str | None
        An optional salt to use in the hash comparison.

    Returns
    -------
    bool
        True if the fingerprint matches the hash, False otherwise.
    """
    return hash_fingerprint(fingerprint, salt=salt) == fingerprint_hash
