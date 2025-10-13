"""
utils for creating, encoding, decoding, and validating JWT tokens.

if for whatever reason you need to update authentication, please
read the resources below:

https://pentesterlab.com/blog/jwt-vulnerabilities-attacks-guide

"""

import uuid
from datetime import UTC, datetime

import msgspec
from jose import JWTError, jwt

from range_monitor.auth.schema import JwtClaim
from range_monitor.core.enums import UserRoles
from range_monitor.infra.security import JwtPolicy


def generate_jti() -> str:
    return uuid.uuid4().hex


def create_jwt_claim(
    policy: JwtPolicy, token_type: str, *, user_id: str, cver: int, role: UserRoles
) -> JwtClaim:
    expires_delta = policy.get_token_ttl(token_type)
    now = datetime.now(UTC)
    expires = now + expires_delta
    return JwtClaim(
        iss=policy.issuer,
        sub=user_id,
        aud=policy.audience,
        iat=int(now.timestamp()),
        exp=int(expires.timestamp()),
        nbf=int(now.timestamp()),
        jti=generate_jti(),
        token_type=token_type,
        cver=cver,
        role=role,
    )


def encode_jwt_payload(policy: JwtPolicy, claims: dict) -> str:
    return jwt.encode(
        claims,
        policy.jwt_secret,
        algorithm=policy.alg,
        headers=policy.token_headers,
    )


def decode_jwt_token(policy: JwtPolicy, token: str) -> dict:
    # header forgery mitigation
    headers = jwt.get_unverified_header(token)
    if not policy.verify_headers(headers):
        raise JWTError('invalid_token_headers')

    return jwt.decode(
        token,
        policy.jwt_secret,
        algorithms=[policy.alg],
        options=policy.decode_options,
        audience=policy.audience,
        issuer=policy.issuer,
    )


def create_claim(
    policy: JwtPolicy, token_type: str, *, user_id: str, cver: int, role: UserRoles
) -> tuple[str, JwtClaim]:
    """
    Creates a JWT token and its associated claims.

    Parameters
    ----------
    policy : JwtPolicy
    token_type : str
    user_id : str
    cver : int
    role : UserRoles

    Returns
    -------
    tuple[str, JwtClaim]
        The encoded JWT token and its claims.
    """
    claim = create_jwt_claim(policy, token_type, user_id=user_id, cver=cver, role=role)
    token = encode_jwt_payload(policy, claim.payload())
    return token, claim


def resolve_claim(
    claims: dict,
    *,
    expected_type: str,
) -> JwtClaim:
    """
    Validates and converts a dictionary of claims into a JwtClaim object.

    Parameters
    ----------
    claims : dict
    expected_type : str

    Returns
    -------
    JwtClaim

    Raises
    ------
    ValueError
        If the claims are invalid or cannot be converted.
    TypeError
        If the token type does not match the expected type.
    """
    try:
        claim = msgspec.convert(claims, JwtClaim)
    except msgspec.ValidationError:
        raise ValueError('token_invalid')

    if claim.token_type != expected_type:
        raise TypeError('token_type_mismatch')

    return claim


def get_token_jti(token: str) -> str | None:
    try:
        unverified_claims = jwt.get_unverified_claims(token)
    except JWTError:
        return None

    return unverified_claims.get('jti')
