from app.shared.errors import HTTPBadRequest, HTTPForbidden, HTTPNotFound


class UserNotFound(HTTPNotFound):
    """404 Not Found"""

    def __init__(self) -> None:
        super().__init__("User")


class UsernameTaken(HTTPBadRequest):
    """400 Bad Request"""

    def __init__(self) -> None:
        super().__init__("This username is already taken")


class DeleteSelfForbidden(HTTPForbidden):
    """when a user tries to delete themselves"""

    def __init__(self) -> None:
        super().__init__("You cannot delete yourself")


class InvalidPermissions(HTTPForbidden):
    """when a user tries to perform an action they do not have permissions for"""

    def __init__(self) -> None:
        super().__init__(
            "You do not have the required permissions to perform this action"
        )


class UserSessionInvalid(HTTPForbidden):
    """when a users session is invalid or tampered with"""

    def __init__(self) -> None:
        super().__init__(
            "The user this session corresponds to either does not exist or did not authorize this session"
        )
