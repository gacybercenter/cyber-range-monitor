from typing import Dict

from fastapi import status
from typing import Annotated, Dict, List, Type


from app.common.errors import HTTPErrorResponse, HTTPValidationError
from pydantic import BaseModel, Field

'''NOTE
package cleanly reduces OpenAPI response annotations without the boilerplate
so all responses and errors can be defined in one place and reused.
'''


class ResponseHint(BaseModel):
    description: Annotated[str, Field(
        ...,
        description='The description of the response'
    )]

    model: Annotated[Type[BaseModel], Field(
        ...,
        description='The pydantic model of the response'
    )]

    headers: Annotated[Dict[str, Dict] | None, Field(
        default=None,
        description='The headers of the response'
    )]

    title: Annotated[str | None, Field(
        default=None,
        description='The title of the response'
    )] = None

    status_code: Annotated[int, Field(
        default=status.HTTP_200_OK,
        description='The status code of the response'
    )] = 200

    def scheme(self) -> Dict:
        '''Formats the response doc into a dict for the OpenAPI spec'''
        if self.title:
            self.description += f'## {self.title}\n{self.description}'
        dumped = self.model_dump(
            exclude={'status_code', 'title'},
            exclude_none=True
        )
        return {
            self.status_code: dumped
        }


def ResponseDoc(
    description: str,
    status_code: int = status.HTTP_200_OK,
    *,
    model: Type[BaseModel],
    headers: dict | None = None,
    title: str | None = None,
) -> Dict:
    '''Defines the response for the OpenAPI spec with the proper details
    (reduce typing), in different case to denote 
    Returns:
        dict -- the additional response data for openapi
    '''
    doc = ResponseHint(
        description=description,
        model=model,
        headers=headers,
        title=title,
        status_code=status_code
    )
    return doc.scheme()


def ErrorDoc(
    description: str,
    status_code: int = status.HTTP_400_BAD_REQUEST,
    *,
    model: Type[BaseModel] | None = None,
    headers: dict | None = None,
    title: str | None = None
) -> Dict:
    '''Defines the response for the OpenAPI spec with the proper error details
    (reduce typing), in different case to denote 
    Returns:
        Dict -- the additional response data for openapi,
    Usage:

    @app.get('/example', responses=ErrorDoc('Unauthorized', 401),
    })
    async def example():
        return {'example': 'example'}

    '''
    if not model:
        model = HTTPErrorResponse

    doc = ResponseHint(
        description=description,
        model=model,
        headers=headers,
        title=title,
        status_code=status_code
    )
    return doc.scheme()


def APIResponses(
    responses: List[Dict]
) -> Dict:
    '''Defines the responses for the OpenAPI spec with the 
    proper details

    Args:
        responses (List[Tuple[int, Dict]]): _the list of (status_code, ResponseDoc)_

    Returns:
        Dict: The annotated and properly formatted responses for the OpenAPI 
        spec
    '''
    openapi_spec = {}
    for response in responses:
        openapi_spec.update(response)
    return openapi_spec


def SchemaError(
    description: str,
    *,
    model: Type[BaseModel] | None = None,
    headers: dict | None = None,
    title: str | None = None
) -> Dict:
    '''Defines the response for the OpenAPI spec with the proper error details
    (reduce typing), in different case to denote 
    Returns:
        Dict -- the additional response data for openapi,
    '''
    if not model:
        model = HTTPValidationError

    doc = ResponseHint(
        description=description,
        model=model,
        headers=headers,
        title=title
    )
    return doc.scheme()


BASE_UNAUTH_ERROR = (
    'When  _Authorization: bearer **<session_id>**_ is missing in the request header.\n'
    '(i.e unauthenticated request)'
)
BASE_FORBIDDEN_ERROR = (
    'When the session ID is invalid, has expired or reached the max age.'
    ' (i.e. forbidden request)'
)


def AuthErrors() -> Dict:
    return APIResponses([
        ErrorDoc(BASE_UNAUTH_ERROR, 401, title='Not authenticated'),
        ErrorDoc(BASE_FORBIDDEN_ERROR, 403, title='Not authorized')
    ])


def UserAuthErrors(*, extra: Dict | None = None) -> Dict:
    '''The errors for the user and role based authentication routes

    Args:
        extra (Dict | None, optional): _additional errors to add to the response_.

    Returns:
        Dict: _the openapi response doc_
    '''
    unauthorized_desc = f'{BASE_UNAUTH_ERROR}\nIf the user no longer exists with a session.'
    forbidden_desc = f'{BASE_FORBIDDEN_ERROR}\nIf the user lacks the role / permission for the route'

    responses = APIResponses([
        ErrorDoc(unauthorized_desc, 401, title='Not authenticated'),
        ErrorDoc(forbidden_desc, 403, title='Not authorized')
    ])

    if extra:
        responses.update(extra)
    return responses


def NotFound(resource: str) -> Dict:
    return ErrorDoc(f'When {resource} does not exist.')
