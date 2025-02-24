from fastapi import HTTPException


class UserNotAuthorized(HTTPException):
    def __init__(self, detail: str) -> None:
        super().__init__(status_code=403, detail=detail)

class UserNotFound(HTTPException):
    def __init__(self) -> None:
        super().__init__(status_code=404, detail='User not found')
        
class UsernameTaken(HTTPException):
    def __init__(self, username: str) -> None:
        super().__init__(status_code=400, detail=f'Username "{username}" is already taken')
        
        