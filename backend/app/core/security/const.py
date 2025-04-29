

PBKDF2_ITERATIONS = 100_000
PBKDF2_KEY_LENGTH = 32

HTTP_BEARER_DESCRIPTION: str = (
    '# Session ID Bearer \n'
    'Uses an **Session ID** that is issued to authenticated clients '
    ' that is digitally signed by the server and stateless until'
    ' presented to the server where it is then resolved to an authenticated user.\n'
    '- The Session ID will expires after a short amount of time (1hr) however it is extended.'
    ' by another hour each time a request is sent and is valid until the max lifetime is reached '
    'requiring the user to reauthenticated.\n'
    '- The Session ID is sent in the request to the API in the `Authorization` header.\n'
)
