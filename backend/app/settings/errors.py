from pydantic import ValidationError
from pydantic_core import ErrorDetails


def string_error_detail(detail: ErrorDetails) -> str:
    '''the details extracted from a pydantic error
    Arguments:
        detail {ErrorDetails} 
    Returns:
        str 
    '''
    return (
        f'ErrorType: {detail['type']}'
        f'\n\tFields: {detail['loc']}'
        f'\n\tMessages: {detail['msg']}'
        f'\n\tInput: {detail['input']}'
    )


def normalize_pydantic_exc(exc: Exception | ValidationError) -> str:
    '''human readable error message for pydantic errors which have horrible formatting
    Returns:
        str -- human readable error message
    '''
    if not isinstance(exc, ValidationError):
        return str(exc)
    normalized_str = '\n'.join([
        string_error_detail(err) for err in exc.errors()
    ])
    return f'\nDetails:\n{normalized_str}'


class InvalidConfigYAML(Exception):
    '''raised when the config.yml file is invalid or missing
    '''
    def __init__(self, details: Exception | ValidationError) -> None:
        details_str = normalize_pydantic_exc(details)
        super().__init__(
            'InvalidConfigYAML: The config.yml file contains invalid or missing '
            f'fields or the file is missing. \n{details_str}'
        )


class SecretsNotFound(Exception):
    '''raised when the secrets .env file or environment variables is invalid, missing
    or not set
    '''
    def __init__(self, path: str) -> None:
        super().__init__(
            'SecretsNotFound: The api secrets could not be resolved'
            ' most likely due to the .env file not being present or a validation error occured'
            ' ensure that either environment variables are set '
            ' or a .env file is present that correspond to the properties and types'
            f' of the secrets model.\nPath={path}'
        )
