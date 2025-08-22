
from itsdangerous import URLSafeSerializer

from app.core import settings


def _create_serializer() -> URLSafeSerializer:
    crypto_settings = settings.get_api_settings().crypto
    return URLSafeSerializer(
        secret_key=crypto_settings.SECRET_KEY,
        salt=crypto_settings.SIGNATURE_SALT,
    )

_serializer = _create_serializer()


def sign_str(input_str: str) -> str:
    """
    Signs a string using the configured secret key and salt.

    Parameters
    ----------
    input_str : str
        The string to sign.

    Returns
    -------
    str
        The signed string.
    """
    return _serializer.dumps(input_str)


def load_signed_str(signed_str: str, *, max_age: int | None = None) -> str | None:
    """
    Loads a signed string, verifying its signature.

    Parameters
    ----------
    signed_str : str
        The signed string to verify and load.

    Returns
    -------
    str
        The original string if the signature is valid.

    Raises
    ------
    BadSignature
        If the signature is invalid.
    """
    try:
        return _serializer.loads(signed_str, max_age=max_age)
    except Exception:
        return None