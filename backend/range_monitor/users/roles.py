from enum import StrEnum


class UserRoles(StrEnum):
    ADMIN = 'admin'
    USER = 'user'
    GUEST = 'guest'


    def __gt__(self, other: 'UserRoles') -> bool:
        return RoleLevels.get_level(self) > RoleLevels.get_level(other)

    def __ge__(self, other: 'UserRoles') -> bool:
        return RoleLevels.get_level(self) >= RoleLevels.get_level(other)

    def __lt__(self, other: 'UserRoles') -> bool:
        return RoleLevels.get_level(self) < RoleLevels.get_level(other)

    def __le__(self, other: 'UserRoles') -> bool:
        return RoleLevels.get_level(self) <= RoleLevels.get_level(other)

class RoleLevels:
    LEVELS = {
        UserRoles.ADMIN: 3,
        UserRoles.USER: 2,
        UserRoles.GUEST: 1,
    }

    @classmethod
    def get_level(cls, role: UserRoles) -> int:
        return cls.LEVELS.get(role, 0)




