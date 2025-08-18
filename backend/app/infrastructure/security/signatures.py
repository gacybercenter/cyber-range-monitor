import functools
import secrets

from fastapi import HTTPException, Request, status
from fastapi.security import HTTPBearer
from fastapi.security.utils import get_authorization_scheme_param
from itsdangerous import BadSignature, SignatureExpired, URLSafeSerializer

from app.core.singletons import SingletonMeta

from .settings import get_crypto_settings


@functools.lru_cache(maxsize=1)
def get_id_signer() -> URLSafeSerializer:
    settings = get_crypto_settings()
    return URLSafeSerializer(
        secret_key=settings.SECRET_KEY,
        salt=settings.SIGNATURE_SALT,
    )

class IdSignerService(metaclass=SingletonMeta):

    def __init__(self) -> None:
        settings = get_crypto_settings()
        self._signer: URLSafeSerializer = URLSafeSerializer(
            secret_key=settings.SECRET_KEY,
            salt=settings.SIGNATURE_SALT,
        )

    def generate_unsigned_id(self) -> str:
        return secrets.token_urlsafe(32)

    def sign_id(self, unsigned_id: str) -> str:
        """
        Signs the given unsigned session ID.
        """
        return self._signer.dumps(unsigned_id)

    def load_signed_id(
        self,
        signed_id: str,
        *,
        max_age: int | None = None,
    ) -> str | None:
        """
        Loads the session ID from the signed ID.
        """
        try:
            return self._signer.loads(signed_id, max_age=max_age)
        except (BadSignature, SignatureExpired):
            return None





