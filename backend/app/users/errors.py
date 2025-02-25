from app.shared.errors import HTTPForbidden, HTTPNotFound, HTTPBadRequest



class UserNotFound(HTTPNotFound):
    def __init__(self) -> None:
        super().__init__("User")
    
class UsernameTaken(HTTPBadRequest):
    def __init__(self) -> None:
        super().__init__("This username is already taken")
        
class DeleteSelfForbidden(HTTPForbidden):
    def __init__(self) -> None:
        super().__init__("You cannot delete yourself")

class InvalidPermissions(HTTPForbidden):
    def __init__(self) -> None:
        super().__init__("You do not have the required permissions to perform this action")

class UserSessionInvalid(HTTPForbidden):
    def __init__(self) -> None:
        super().__init__("The user this session corresponds to either does not exist or did not authorize this session")