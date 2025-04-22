
from typing import Self

from .const import (
    KEY_INJECTION_RE, VALID_KEY_RE, MAX_KEY_LENGTH
)
from .errors import InvalidRedisKey


def validate_key_input(key: str) -> str:
    '''optimized sanitization function using precompiled regexes to 
    verify a key before it's passed is not invalid or an attempted
    injection attack.
    
    Arguments:
        key {str} -- the key to sanitize and prepend the  prefix to
        prefix {str | None} -- the optional prefix to prepend to the key
    Returns:
        str -- the validated key 
    '''
    if not key:
        raise InvalidRedisKey()
    
    key = key.strip()
    if not key or len(key) > MAX_KEY_LENGTH:
        raise InvalidRedisKey() 
    
    if not VALID_KEY_RE.match(key):
        raise InvalidRedisKey()

    if KEY_INJECTION_RE.search(key):
        raise InvalidRedisKey()
    
    return key


class RedisKey(str):
    '''string wrapper with built in sanitization for automatic safety
    for the user of the client requiring sanitization to be performed
    '''
    def __new__(cls, value: str, prefix: str | None = None) -> Self:
        val = validate_key_input(value)
        if prefix:
            val = f'{prefix}:{val}'
        return super().__new__(cls, val)
