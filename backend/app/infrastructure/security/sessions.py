import secrets
import time
from dataclasses import dataclass
from typing import Any, Self

from fastapi import Request
from fastapi.security.oauth2 import OAuth2PasswordBearer
from fastapi.security.utils import get_authorization_scheme_param
from itsdangerous import BadSignature, SignatureExpired, URLSafeSerializer
from pydantic import BaseModel, Field

from .settings import get_crypto_settings


def _create_serializer() -> URLSafeSerializer:
    crypto_settings = get_crypto_settings()
    return URLSafeSerializer(
        secret_key=crypto_settings.SECRET_KEY,
        salt=crypto_settings.SIGNATURE_SALT,
    )


_serializer = _create_serializer()


def utcnow() -> int:
    return int(time.time())


def _create_signature(data: str) -> str:
    """
    Parameters
    ----------
    data : str

    Returns
    -------
    str
    """
    return _serializer.dumps(data)


def _load_signature(
    signed_data: str,
    *,
    max_age: int | None = None,
) -> str | None:
    """
    Verifies and loads the original data from the signed input.

    Parameters
    ----------
    signed_data : str
    max_age : int | None, optional
        _in seconds_, by default None

    Returns
    -------
    str | None
        _None if max age is reached or invalid_
    """
    signer = _serializer
    try:
        unsigned_payload = signer.loads(signed_data, max_age=max_age)
    except (SignatureExpired, BadSignature):
        return None

    return unsigned_payload


def create_session_id() -> str:
    return secrets.token_urlsafe(32)


@dataclass(slots=True)
class SessionId:
    signed_id: str
    unsigned_id: str | None = None

    @property
    def signature_invalid(self) -> bool:
        """
        Checks if the signature is invalid or expired.

        Returns
        -------
        bool
            True if the signature is invalid or expired, False otherwise.
        """
        return self.unsigned_id is None

    @classmethod
    def create(cls) -> Self:
        """
        Creates a new SessionId instance with a signed ID.

        Returns
        -------
        SessionId
            A new SessionId instance with a signed ID.
        """
        raw_id = create_session_id()
        signed_id = _create_signature(raw_id)
        return cls(signed_id=signed_id, unsigned_id=raw_id)

    @classmethod
    def load(cls, signed_id: str) -> Self:
        """
        Loads a SessionId instance from a signed ID.

        Parameters
        ----------
        signed_id : str
            The signed ID to load.

        Returns
        -------
        SessionId
            A SessionId instance with the loaded signed ID.
        """
        unsigned_id = _load_signature(signed_id) or 'MISSING'
        return cls(signed_id=signed_id, unsigned_id=unsigned_id)



class SessionSecurity(OAuth2PasswordBearer):
    _DESCRIPTION = (
        'Custom implementation of OAuth2PasswordBearer that uses session IDs '
        'instead of access tokens (_so we get token URL in docs_).\n\n'
        'This class is a dependency and as a dependency it simply checks for the '
        'session ID in the request header, removes the signature and returns it.\n\n'
        'It does not raise an exception and is the responsibility of the caller to '
        'handle the absence of the session ID or invalid signatures.'
    )

    def __init__(self) -> None:
        super().__init__(
            tokenUrl='/auth/login',
            auto_error=False,
            description=self._DESCRIPTION,
            scheme_name=self.__class__.__name__,
        )

    async def __call__(self, request: Request) -> SessionId | None:
        """
        Extracts the session ID from the request headers. Does not raise an error
        or check if the session ID is valid or not.
        Parameters
        ----------
        request : Request
            _The request sent by the client_

        Returns
        -------
        SessionId | None
        """
        authorization: str | None = request.headers.get('Authorization')
        if not authorization:
            return None

        scheme, signed_id = get_authorization_scheme_param(authorization)
        if scheme.lower() != 'session':
            return None

        return SessionId.load(signed_id)


SessionIdSecurity = SessionSecurity()
