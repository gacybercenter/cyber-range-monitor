from typing import Annotated

from fastapi import Security

from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer


oauth_key_bearer = HTTPBearer(
    auto_error=False,
    description=(
        '# API Key Bearer \n'
        'Uses an **API Key** that is issued to authenticated clients '
        ' that is digitally signed by the server and stateless until'
        ' presented to the server where it is then resolved to an authenticated user.\n'
        '- The API Key will expires after a short amount of time (1hr) however it is extended.'
        ' by another hour each time a request is sent and is valid until the max lifetime is reached '
        'requiring the user to reauthenticated.\n'
        '- The API Key is sent in the request to the API in the `Authorization` header.\n'
    ),
)

KeyBearerSecurityDep = Annotated[HTTPAuthorizationCredentials, Security(oauth_key_bearer)]