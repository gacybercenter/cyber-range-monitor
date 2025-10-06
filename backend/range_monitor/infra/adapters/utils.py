




import dataclasses as dc
import hashlib
from typing import Any


def hash_dataclass(data_cls: Any) -> bytes:
    '''
    Hashes a dataclass instance into a SHA-256 hash.

    Parameters
    ----------
    dc : Any
        _A dataclass instance_

    Returns
    -------
    bytes
        _The SHA-256 hash of the dataclass instance_
    '''
    if not dc.is_dataclass(data_cls):
        raise ValueError('Input must be a dataclass instance.')

    dumped = dc.asdict(data_cls) # type: ignore
    hash_input = ''.join(
        f'{k}={v};'
        for k, v in sorted(dumped.items())
        if v is not None
    )

    return hashlib.sha256(hash_input.encode('utf-8')).digest()

def compare_dataclass(stored: object | bytes, current: object) -> bool:
    '''
    Compares a stored dataclass hash with the hash of a current dataclass instance.
    Parameters
    ----------
    stored : object | bytes
        The stored dataclass instance or its hash
    current : object
        The current dataclass instance to compare against
    Returns
    -------
    bool
        True if the hashes match, False otherwise
    '''
    if isinstance(stored, bytes):
        stored_hash = stored
    elif dc.is_dataclass(stored):
        stored_hash = hash_dataclass(stored) # type: ignore
    else:
        raise ValueError('Stored value must be a dataclass instance or bytes.')

    return stored_hash == hash_dataclass(current) # type: ignore