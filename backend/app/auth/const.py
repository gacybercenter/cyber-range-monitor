
from fastapi.security import APIKeyCookie


AUTH_MODEL_DESC = (
    "Raises a 403 if the name (API_KEY_COOKIE_NAME) cookie is missing "
    " or invalid and returns the value of the cookie which for this auth model "
    " is a signed APIKey which is resolved to data stored in redis. "
)
AUTH_COOKIE_NAME = 'api_key'
API_KEY_AUTH_MODEL = APIKeyCookie(
    name=AUTH_COOKIE_NAME,
    auto_error=False,
    description=AUTH_MODEL_DESC
)
