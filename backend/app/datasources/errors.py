from app.shared.errors import HTTPBadRequest, HTTPNotFound


class DatasourceToggleError(HTTPBadRequest):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class DatasourceNotFound(HTTPNotFound):
    def __init__(self) -> None:
        super().__init__("Datasource not found")
