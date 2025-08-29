

import abc
from typing import Generic, Self, TypeVar

_T = TypeVar('_T')

class ConnectionSpec(abc.ABC, Generic[_T]):
    @abc.abstractmethod
    @classmethod
    def create_from_source(cls, datasource: _T, plaintext_password: str) -> Self:
        pass
