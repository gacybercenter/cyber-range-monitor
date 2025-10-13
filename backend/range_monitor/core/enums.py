from enum import StrEnum
from types import MappingProxyType


class UserRoles(StrEnum):
    ADMIN = 'admin'
    USER = 'user'
    GUEST = 'guest'

    def __gt__(self, other: 'UserRoles') -> bool:
        return self.level > other.level

    def __ge__(self, other: 'UserRoles') -> bool:
        return self.level >= other.level

    def __lt__(self, other: 'UserRoles') -> bool:
        return self.level < other.level

    def __le__(self, other: 'UserRoles') -> bool:
        return self.level <= other.level

    @property
    def level(self) -> int:
        return get_role_level(self)


RoleLevelMap = MappingProxyType(
    {
        UserRoles.ADMIN: 3,
        UserRoles.USER: 2,
        UserRoles.GUEST: 1,
    }
)


def get_role_level(role: UserRoles) -> int:
    return RoleLevelMap.get(role, 0)


class APISources(StrEnum):
    GUACAMOLE = 'guacamole'
    OPENSTACK = 'openstack'
    SALTSTACK = 'saltstack'
