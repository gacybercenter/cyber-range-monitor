from pydantic import BaseModel, Field
from api.models.user import UserRoles
from typing import Optional


class SchemaCheck:
    '''
        static methods to check the validity of the pydantic models 
    '''

    @staticmethod
    def check_permission(user_permission: str) -> None:
        assert user_permission in [
            perm.value for perm in UserRoles
        ], ERROR_MSG.UNKNOWN_ROLE

    @staticmethod
    def no_space(field: str, field_name: str) -> None:
        assert not ' ' in field, f'{field_name} {ERROR_MSG.HAS_SPACE}'

    @staticmethod
    def check_api_version(api_vers: str) -> None:
        assert all([
                char.isdigit() for char in api_vers
            ]), ERROR_MSG.BAD_API_VERSION



class ERROR_MSG:
    INVALID_ROLE = 'You do not have permission to assign this role'
    UNKNOWN_ROLE = 'Cannot assign an unkown role to a user'
    HAS_SPACE = 'Field cannot contain space'

    BAD_API_VERSION = 'API version must be a string of digits'

class DatasourceReadBase(BaseModel):
    id: int
    username: str
    password: str
    enabled: bool


class DatasourceCreateBase(BaseModel):
    id: int = Field(..., ge=1)
    username: str = Field(..., min_length=1, max_length=255)
    password: str = Field(..., min_length=1, max_length=255)
    enabled: bool = Field(False)


class DatasourceUpdateBase(BaseModel):
    id: Optional[int] = Field(None, ge=1)
    username: Optional[str] = Field(None, min_length=1, max_length=255)
    password: Optional[str] = Field(None, min_length=1, max_length=255)

