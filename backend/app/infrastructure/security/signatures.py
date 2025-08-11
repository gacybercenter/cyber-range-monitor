from itsdangerous import URLSafeSerializer
from itsdangerous import SignatureExpired, BadSignature

def _create_serializer() -> URLSafeSerializer:
    """Initializes the URLSafeSerializer with the secret key and salt.

    Returns:
        URLSafeSerializer -- The URLSafeSerializer instance.
    """
    from .settings import get_crypto_settings_sync

    crypto_settings = get_crypto_settings_sync()
    return URLSafeSerializer(
        secret_key=crypto_settings.SECRET_KEY,
        salt=crypto_settings.SIGNATURE_SALT,
    )


_serializer = _create_serializer()


class SignatureService:
    def __init__(
        self,
        signature_salt: str,
        *,
        serializer: URLSafeSerializer = _serializer,
    ) -> None:
        self._serializer: URLSafeSerializer = serializer
        self._signature_salt: str = signature_salt

    def create_signature(self, data: str) -> str:
        """
        Creates a signature for the given data.

        Parameters
        ----------
        data : dict
            The data to sign.

        Returns
        -------
        str
            The generated signature.
        """
        return self._serializer.dumps(data, salt=self._signature_salt)

    def load_signature(self, signed_data: str, *, max_age: int | None = None) -> str | None:
        """
        Loads and verifies the signature.

        Parameters
        ----------
        signed_data : str
            The signed data to verify.

        Returns
        -------
        str | None
            The original data if the signature is valid.
            If the signature is invalid or expired, returns None.
        Raises
        ------
        SignatureExpired
            If the signature has expired.
        BadSignature
            If the signature is invalid.
        """

        try:
            unsigned_payload = self._serializer.loads(
                signed_data,
                salt=self._signature_salt,
                max_age=max_age
            )
        except (SignatureExpired, BadSignature) as e:
            return None

        return unsigned_payload


async def get_signature_service(signature_salt: str) -> SignatureService:
    """
    Dependency wrapper for SignatureService.

    Parameters
    ----------
    signature_salt : str

    Returns
    -------
    SignatureService
    """
    return SignatureService(
        signature_salt=signature_salt,
        serializer=_serializer
    )