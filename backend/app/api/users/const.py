from app.misc.openapi_extra import err_response_doc
from typing import Dict


ADMIN_DELETES_SELF: Dict = {
    403: err_response_doc("An admin cannot delete their own account.")
}
USERNAME_TAKEN_RESPONSE: Dict = {
    400: err_response_doc("The username provided is taken.")
}
