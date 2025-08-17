import functools
import secrets
import time
from dataclasses import dataclass
from typing import Self
from typing_extensions import Annotated, Doc
from pydantic import BaseModel, Field
from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer
from fastapi.security.oauth2 import OAuth2PasswordBearer
from fastapi.security.utils import get_authorization_scheme_param
from itsdangerous import BadSignature, SignatureExpired, URLSafeSerializer
from test.test_typing import Annotated

from .settings import get_crypto_settings


@functools.lru_cache(maxsize=1)
def get_id_signer() -> URLSafeSerializer:
    settings = get_crypto_settings()
    return URLSafeSerializer(
        secret_key=settings.SECRET_KEY,
        salt=settings.SIGNATURE_SALT,
    )


@dataclass(slots=True)
class SessionID:
    unsigned_id: str

    @classmethod
    def generate(cls, *, key_length: int = 32) -> Self:
        """
        creates unsigned session ID
        """
        return cls(unsigned_id=secrets.token_urlsafe(key_length))

    def sign(self, *, signer: URLSafeSerializer | None = None) -> str:
        """
        signs the session ID
        """

        signer = signer or get_id_signer()
        return signer.dumps(self.unsigned_id)

    def load_sid(
        self,
        signed_id: str,
        *,
        max_age: int | None = None,
        signer: URLSafeSerializer | None = None,
    ) -> str | None:
        """
        loads the session ID from the signed ID
        """
        signer = signer or get_id_signer()
        unsigned_id: str | None = None

        try:
            unsigned_id = signer.loads(signed_id, max_age=max_age)
        except (BadSignature, SignatureExpired):
            return None

        return unsigned_id


class SessionBearerOptions(BaseModel):
    scheme_name: Annotated[
        str,
        Field(
            description='The name of the security scheme, used in OpenAPI documentation.'
        ),
    ] = 'HTTPSessionIDBearer'

    unauthorized_msg: Annotated[
        str,
        Field(
            description='Message returned when the session ID is missing',
        ),
    ] = 'You must be authenticated to access this resource.'

    serializer: URLSafeSerializer = Field(
        default_factory=get_id_signer,
        description='Serializer used for signing and verifying session IDs.',
    )

    header_name: Annotated[
        str,
        Field(description='The name of the HTTP header used to get the session ID.'),
    ] = 'Authorization'

    @property
    def description(self) -> str:
        return (
            f'Expects the client to send a session ID signed by the server '
            f'in the `{self.header_name}` header. The session ID is signed using '
            'the secret key that corresponds to a session. This dependency simply '
            'extracts the session ID and attaches the `SessionID` object in the '
            ' request state and returns it as a dependency result.\n\n'
            'If the session ID is not present or not in the bearer format, '
            f'the server will respond with a 401 message: `{self.unauthorized_msg}`.'
        )


class HTTPSessionIdMissing(HTTPException):
    def __init__(self, message: str, header: dict | None) -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=message or 'Session ID is missing.',
            headers=header or {'WWW-Authenticate': 'Bearer'},
        )


class HTTPSessionIDBearer(HTTPBearer):
    def __init__(self, options: SessionBearerOptions) -> None:
        super().__init__(
            scheme_name=options.scheme_name,
            description=options.description,
            auto_error=True,
        )
        self.signer: URLSafeSerializer = options.serializer
        self.header_name: str = options.header_name
        self.unauthorized_msg: str = options.unauthorized_msg

    async def __call__(self, request: Request) -> SessionID:
        authorization = request.headers.get(self.header_name)
        if not authorization:
            raise HTTPSessionIdMissing(
                message=self.unauthorized_msg,
                header={'WWW-Authenticate': 'Bearer'},
            )

        scheme, unsigned_sid = get_authorization_scheme_param(authorization)
        if not unsigned_sid or scheme.lower() != 'bearer':
            raise HTTPSessionIdMissing(
                message=self.unauthorized_msg,
                header={'WWW-Authenticate': 'Bearer'},
            )
        return SessionID(unsigned_id=unsigned_sid)
