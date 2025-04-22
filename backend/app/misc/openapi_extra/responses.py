from fastapi import status
from typing import Dict


from app.core.errors import APIErrorResponse, HTTPValidationErrorDetails
from fastapi.background import P


# NOTE: This module defines the response schemas for the OpenAPI spec allowing
# for clearer types and response definitions for the generated API Client


def err_response_doc(description: str) -> dict:
    '''Defines the response for the OpenAPI spec with the proper error details
    (reduce typing)
    Returns:
        dict -- the additional response data for openapi
    '''
    return { "description": description, "model": APIErrorResponse }


PYDANTIC_SCHEMA_ERROR: Dict = {
    422: {
        'description': 'Pydantic raises due to improper data being provided',
        'model': HTTPValidationErrorDetails,
    }
}

NOT_FOUND_404: Dict = {
    status.HTTP_404_NOT_FOUND: err_response_doc(
        f"Resource not found / doesn't exist."
    )
}

AUTH_DEP_RESPONSES: Dict = {
    status.HTTP_401_UNAUTHORIZED: err_response_doc('When the user does not provide an API Key'),
    status.HTTP_403_FORBIDDEN: err_response_doc('When the API Key is invalid'),
    status.HTTP_406_NOT_ACCEPTABLE: err_response_doc(
        'The users API Key was tampered with in a way it would attempt a Redis Key Injection.'
    )
}

USER_DEP_RESPONSE = {
    status.HTTP_401_UNAUTHORIZED: err_response_doc('When the users API Key corresponds to a user that does not exist'),
    **AUTH_DEP_RESPONSES
}

ROLE_REQUIRED_DEP_RESPONSE = {
    status.HTTP_403_FORBIDDEN: err_response_doc('When the user does not have the required role to access the resource'),
    **USER_DEP_RESPONSE
}

def response_model_union_doc(
    desc: str,
    one_of: list[dict],
    status_code: int = status.HTTP_200_OK 
) -> Dict:
    '''Defines cases where multiple response types are returned to the client 

    Arguments:
        desc {str} -- the description of the response
        one_of {list[dict]} -- the list of schemas that are returned 
        in the response

    Keyword Arguments:
        status_code {int} -- the status code returned, default  {200}

    Returns:
        Dict -- the union response schema for the OpenAPI spec
    '''
    return {
        status_code: {
            'description': desc,
            'content': {
                'application/json': {
                    'schema': {
                        'oneOf': one_of
                    }
                }
            }
        }
    }
    
    
    
    
    


