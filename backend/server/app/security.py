'''
utils for creating, encoding, decoding, and validating JWT tokens.

if for whatever reason you need to update authentication, please
read the resources below:

https://pentesterlab.com/blog/jwt-vulnerabilities-attacks-guide

'''
from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING, Final

from cryptography.fernet import Fernet
from itsdangerous import URLSafeTimedSerializer
from jose import JWTError, jwt
from pwdlib import PasswordHash

from server.db.redis import get_app_settings
from server.settings import get_secret_settings

if TYPE_CHECKING:
    from server.configs.secrets import SecretSettings
    from server.enums import UserRoles


@dataclass(slots=True)
class Token:
    claim: dict
    encoded: str
    expires: datetime
    issued_at: datetime
    exp_delta: timedelta

    @property
    def exp(self) -> int:
        return int(self.exp_delta.total_seconds())


def generate_jti() -> str:
    return uuid.uuid4().hex


def utcnow() -> datetime:
    return datetime.now(UTC)


def encode_jwt_token(payload: dict) -> str:
    secrets = get_secret_settings()
    get_app_settings().auth
    return jwt.encode(
        payload,
        secrets.jwt_private_key.get_secret_value(),
        algorithm=secrets.jwt_algorithm,
        headers={
            'kid': secrets.jwt_kid,
            'typ': 'JWT',
        },
    )


def decode_jwt_token(token: str) -> dict:
    secrets = get_secret_settings()
    auth_conf = get_app_settings().auth
    headers = jwt.get_unverified_header(token)
    kid = headers.get('kid')
    if kid != secrets.jwt_kid:
        raise JWTError('invalid_or_expired_kid')

    return jwt.decode(
        token,
        secrets.jwt_public_key.get_secret_value(),
        algorithms=[secrets.jwt_algorithm],
        issuer=auth_conf.jwt_issuer,
        audience=auth_conf.jwt_audience,
        options={
            'require_aud': True,
            'require_iss': True,
            'require_sub': True,
            'require_iat': True,
            'require_exp': True,
            'require_nbf': True,
            'leeway': auth_conf.token_leeway_seconds,
        },
    )


def get_base_jwt_claims(
    user_id: uuid.UUID,
    cver: int,
    sid: str,
) -> dict:
    now = utcnow()
    auth_conf = get_app_settings().auth
    return {
        'sub': str(user_id),
        'iat': int(now.timestamp()),
        'nbf': int(now.timestamp()),
        'iss': auth_conf.jwt_issuer,
        'aud': auth_conf.jwt_audience,
        'cver': cver,
        'sid': sid,
    }


def create_access_token(
    base_claims: dict,
    role: UserRoles,
    username: str,
) -> Token:
    auth_conf = get_app_settings().auth
    exp = utcnow() + auth_conf.access_token_exp
    to_encode = base_claims.copy()
    to_encode.update({
        **base_claims,
        'scope': role.value,
        'jti': generate_jti(),
        'exp': int(exp.timestamp()),
        'username': username,
        'token_type': 'access',
    })

    encoded = encode_jwt_token(to_encode)
    return Token(
        claim=to_encode,
        encoded=encoded,
        expires=exp,
        issued_at=base_claims['iat'],
        exp_delta=auth_conf.access_token_exp,
    )


def create_refresh_token(
    base_claims: dict,
) -> Token:
    auth_conf = get_app_settings().auth
    exp = utcnow() + auth_conf.refresh_token_exp
    to_encode = base_claims.copy()
    to_encode.update({
        **base_claims,
        'exp': int(exp.timestamp()),
        'jti': generate_jti(),
        'token_type': 'refresh',
    })

    encoded = encode_jwt_token(to_encode)
    return Token(
        claim=to_encode,
        encoded=encoded,
        expires=exp,
        issued_at=base_claims['iat'],
        exp_delta=auth_conf.refresh_token_exp,
    )


def decode_token_strict(
    token: str,
    *,
    token_type: str
) -> dict:
    claims = decode_jwt_token(token)
    if claims.get('token_type') != token_type:
        raise TypeError('token_type_mismatch')
    return claims


def create_fernet_cipher(*, secrets: SecretSettings | None = None) -> Fernet:
    secrets = secrets or get_secret_settings()
    return Fernet(secrets.derived_key)


def create_password_hasher(*, secrets: SecretSettings | None = None) -> PasswordHash:
    secrets = secrets or get_secret_settings()
    return PasswordHash((
        secrets.agron2_hasher,
    ))


def create_signer(*, secrets: SecretSettings | None = None) -> URLSafeTimedSerializer:
    secrets = secrets or get_secret_settings()
    return URLSafeTimedSerializer(
        secrets.csrf_secret.get_secret_value(),
        salt=secrets.csrf_salt.get_secret_value()
    )


_fernet_cipher: Final[Fernet] = create_fernet_cipher()
_password_hasher: Final[PasswordHash] = create_password_hasher()
_signer: Final[URLSafeTimedSerializer] = create_signer()


def encrypt_plaintext(plaintext: str) -> bytes:
    token_bytes = plaintext.encode('utf-8')
    return _fernet_cipher.encrypt(token_bytes)


def decrypt_ciphertext(ciphertext: bytes) -> str:
    decrypted_bytes = _fernet_cipher.decrypt(ciphertext)
    return decrypted_bytes.decode('utf-8')


def verify_password(plaintext: str, hashed: str) -> bool:
    return _password_hasher.verify(plaintext, hashed)


def hash_password(plaintext: str) -> str:
    return _password_hasher.hash(plaintext)


def signer_dumps(data: str) -> str:
    return _signer.dumps(data)


def signer_loads(token: str, *, max_age: int | None = None) -> str | None:
    try:
        return _signer.loads(token, max_age=max_age)
    except Exception:
        return None
