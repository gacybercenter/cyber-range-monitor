'''
Contains all of the security policies for the application
that are loaded once at application startup.
'''

import base64
import dataclasses as dc
from datetime import timedelta

from cryptography.fernet import Fernet
from passlib.context import CryptContext

from range_monitor.core.errors import RuntimeAppError
from range_monitor.infra.security import utils as sec_utils
from range_monitor.infra.security._config import CryptoConfig, JwtOptions, JwtSecrets


@dc.dataclass(slots=True, frozen=True)
class JwtPolicy:
    '''
    The policy loaded at application startup that defines
    how JWT tokens are created and validated.

    Raises
    ------
    RuntimeAppError - `get_token_ttl` raises if an unknown token type is requested.
    '''
    jwt_secret: bytes
    issuer: str
    audience: str
    kid: str
    token_expiry: dict[str, timedelta]
    decode_options: dict = dc.field(default_factory=dict)
    token_headers: dict = dc.field(default_factory=dict)

    def get_token_ttl(self, token_type: str) -> timedelta:
        if not (ttl := self.token_expiry.get(token_type)):
            raise RuntimeAppError(
                code='unknown_token_type',
                reason=f'Policy does not include `{token_type}`',
                fix='Check the configuration for token TTLs.'
            )

        return ttl

    def verify_headers(self, headers: dict) -> bool:
        for name, value in self.token_headers.items():
            if name not in headers or headers[name] != value:
                return False
        return True

    @property
    def alg(self) -> str:
        return self.token_headers.get('alg', 'HS256')


@dc.dataclass(slots=True, frozen=True)
class CryptoPolicy:
    bcrypt: CryptContext
    bcrypt_pepper: bytes
    fernet: Fernet

def create_crypto_policy(
    *,
    config: CryptoConfig | None = None,
    temporary: bool = False
) -> CryptoPolicy:

    if temporary:
        config = CryptoConfig(
            fernet_key=sec_utils.generate_fernet_key(),
            bcrypt_pepper=sec_utils.generate_secret_key(16)
        )

    config = config or CryptoConfig()  # type: ignore

    bcrypt = CryptContext(
        schemes=['bcrypt'],
        bcrypt__rounds=config.bcrypt_rounds,
        deprecated='auto'
    )
    pepper = config.bcrypt_pepper.encode('utf-8')

    derived_key = sec_utils.get_derived_key(
        config.fernet_key,
        salt=config.bcrypt_pepper,
        pbkdf2_iterations=config.pbkdf2_iterations,
        pbkdf2_key_length=config.pbkdf2_key_length
    )

    fernet = Fernet(base64.urlsafe_b64encode(derived_key))

    return CryptoPolicy(
        bcrypt=bcrypt,
        bcrypt_pepper=pepper,
        fernet=fernet
    )

def create_jwt_policy(
    *,
    secrets: JwtSecrets | None = None,
    options: JwtOptions | None = None,
    extra_token_ttls: dict[str, timedelta] | None = None,
) -> JwtPolicy:
    secrets = secrets or JwtSecrets()  # type: ignore
    options = options or JwtOptions()  # type: ignore
    ttls = {
        'access': options.access_delta,
        'refresh': options.refresh_delta
    }
    if extra_token_ttls:
        ttls.update(extra_token_ttls)

    return JwtPolicy(
        jwt_secret=secrets.jwt_secret_key.encode('utf-8'),
        issuer=options.jwt_issuer,
        audience=options.jwt_audience,
        kid=secrets.jwt_kid,
        token_expiry=ttls,
        decode_options={
            'require_aud': True,
            'require_iss': True,
            'require_sub': True,
            'require_iat': True,
            'require_exp': True,
            'require_jti': True,
            'require_nbf': True,
            'leeway': options.token_leeway_seconds
        },
        token_headers={
            'kid': secrets.jwt_kid,
            'alg': secrets.jwt_algorithm,
            'typ': 'JWT',
        }
    )


