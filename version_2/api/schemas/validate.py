from api.models.user import UserRoles


class SchemaCheck:

    @staticmethod
    def check_permission(user_permission: str) -> None:
        assert user_permission in [
            perm.value for perm in UserRoles
        ], ERROR_MSG.UNKNOWN_ROLE

    @staticmethod
    def no_space(field: str, field_name: str) -> None:
        assert not ' ' in field, f'{field_name} {ERROR_MSG.HAS_SPACE}'


class ERROR_MSG:
    INVALID_ROLE = 'You do not have permission to assign this role'
    UNKNOWN_ROLE = 'Cannot assign an unkown role to a user'
    HAS_SPACE = 'Field cannot contain space'

    BAD_API_VERSION = 'API version must be a string of digits'
