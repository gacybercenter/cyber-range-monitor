from __future__ import annotations

import contextlib
from typing import TYPE_CHECKING, Any, NamedTuple

from jose import ExpiredSignatureError, JWTError

from server.app import security
from server.app.auth.errors import InvalidTokenError, TokenMissingError
from server.app.auth.repo import TokenKey, TokenStore
from server.app.auth.schema import AccessToken
from server.app.main import get_app_settings

if TYPE_CHECKING:
    from collections.abc import Generator

    from fastapi import Response

    from server.app.auth.schema import RefreshToken
    from server.app.users.schema import InternalUser
    from server.configs.toml import AuthenticationConfig


class TokenPair(NamedTuple):
    access: security.Token
    refresh: security.Token


def create_token_pair(
    user: InternalUser,
    session_id: str,
) -> TokenPair:
    base_claims = security.get_base_jwt_claims(user.id, user.cver, session_id)
    access = security.create_access_token(
        base_claims,
        role=user.role,
        username=user.username
    )
    refresh = security.create_refresh_token(base_claims)
    return TokenPair(access=access, refresh=refresh)


async def verify_token_state(
    token_data: AccessToken | RefreshToken,
    tokens: TokenStore,
) -> TokenKey:
    token_type = 'access' if isinstance(token_data, AccessToken) else 'refresh'
    key = TokenKey(
        token_type,
        token_data.sid,
        str(token_data.sub)
    )
    if not await tokens.exists(key):
        raise InvalidTokenError('token_revoked')

    if not await tokens.verify_cver(token_data.sub, token_data.cver):
        await tokens.delete_session_tokens(
            token_data.sid,
            str(token_data.sub)
        )
        raise InvalidTokenError('token_stale')

    return key


@contextlib.contextmanager
def jwt_error_codes() -> Generator[None, Any]:
    try:
        yield
    except ExpiredSignatureError:
        raise InvalidTokenError('token_expired')
    except (JWTError, ValueError):
        raise InvalidTokenError('token_invalid')
    except TypeError:
        raise InvalidTokenError('invalid_token_type')


def load_jwt_claim(
    token: str | None,
    expected_type: str
) -> dict:
    if not token:
        raise TokenMissingError
    with jwt_error_codes():
        claim = security.decode_token_strict(
            token,
            token_type=expected_type
        )
    return claim


def set_refresh_token_cookie(
    response: Response,
    token: str,
    *,
    config: AuthenticationConfig | None = None
) -> None:
    config = config or get_app_settings().auth
    response.set_cookie(
        key='refresh_token',
        value=token,
        max_age=int(config.refresh_token_exp.total_seconds()),
        domain=config.cookie_domain,
        secure=config.cookie_secure,
        httponly=config.cookie_httponly,
        samesite=config.cookie_samesite,
    )


def delete_refresh_token_cookie(
    response: Response,
    *,
    config: AuthenticationConfig | None = None
) -> None:
    config = config or get_app_settings().auth
    response.delete_cookie(
        key='refresh_token',
        domain=config.cookie_domain,
        secure=config.cookie_secure,
        httponly=config.cookie_httponly,
        samesite=config.cookie_samesite,
    )
