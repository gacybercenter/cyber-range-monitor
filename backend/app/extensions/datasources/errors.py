from app.core.errors import HTTPBadRequest, HTTPNotFound, HTTPInvalidRequestData


class DatasourceToggleError(HTTPBadRequest):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class DatasourceNotFound(HTTPNotFound):
    def __init__(self) -> None:
        super().__init__("Datasource not found")


class InvalidDatasourceSchema(HTTPInvalidRequestData):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class NoEnabledDatasourceError(HTTPBadRequest):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class HTTPDatasourceConnectionFailed(HTTPBadRequest):
    def __init__(self, details: str = '') -> None:
        msg = 'Error: could not establish a connection with the datasource'
        if details:
            msg += f' - {details}'
        super().__init__(msg)
        self.label = "CONNECTION_FAILED"
