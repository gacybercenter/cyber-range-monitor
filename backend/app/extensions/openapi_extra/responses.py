from fastapi import status
from typing import Dict
from app.core.errors.details import APIErrorResponse


# NOTE: This module defines the response schemas for the OpenAPI spec allowing
# for clearer types and response definitions for the generated API Client


def err_response_doc(description: str) -> dict:
    '''Defines the response for the OpenAPI spec with the proper error details
    (reduce typing)
    Returns:
        dict -- the additional response data for openapi
    '''
    return { "description": description, "model": APIErrorResponse }


NOT_FOUND_404: Dict = {
    status.HTTP_404_NOT_FOUND: err_response_doc(f"Resource not found / doesn't exist.")
}

AUTH_DEP_RESPONSES: Dict = {
    status.HTTP_401_UNAUTHORIZED: err_response_doc('When the user does not provide an API Key'),
    status.HTTP_403_FORBIDDEN: err_response_doc('When the API Key is invalid')
}

USER_DEP_RESPONSE = {
    status.HTTP_401_UNAUTHORIZED: err_response_doc('When the users API Key corresponds to a user that does not exist'),
    **AUTH_DEP_RESPONSES
}

ROLE_REQUIRED_DEP_RESPONSE = {
    status.HTTP_403_FORBIDDEN: err_response_doc('When the user does not have the required role to access the resource'),
    **USER_DEP_RESPONSE
}
