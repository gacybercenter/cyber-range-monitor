

from app.core.errors import HTTPBadRequest, HTTPNotFound


class HTTPBadDatasourceType(HTTPBadRequest):
    '''HTTP 400 Bad Request Exception raised when the request body
    uses an unsupported datasource type.
    (e.g) /guacamole/ with => (body: { 'datasource_type': 'openstack' })
    '''

    def __init__(self, input_type: str, expected: str) -> None:
        err_msg = (
            f'Unsupported Operation: You cannot use a datasource type of '
            f'{input_type} for {expected} datasources. '
        )
        super().__init__(err_msg)


class HTTPBadDatasourceToggle(HTTPBadRequest):
    '''HTTP 400 Bad Request Exception raised when the datasource is already enabled.'''

    def __init__(self, already_enabled_username: str) -> None:
        err_msg = (
            'Cannot toggle datasource: The datasource selected '
            f'({already_enabled_username}) is already enabled which would '
            'result in no datasources being enabled. To disable it, please '
            'toggle another datasource.'
        )
        super().__init__(err_msg)


class HTTPDatasourceNotFound(HTTPNotFound):
    '''HTTP 404 Not Found Exception raised when the datasource is not found.'''

    def __init__(self, datasource_type: str) -> None:
        err_msg = (
            f'Datasource not found: The {datasource_type} datasource provided '
            'does not exist.'
        )
        super().__init__('datasource', err_msg)
