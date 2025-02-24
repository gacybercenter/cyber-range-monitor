



from fastapi import HTTPException


class DatasourceNotFound(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=404,
            detail=f'Datasource not found'
        )