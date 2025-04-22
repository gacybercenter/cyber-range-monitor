from datetime import timedelta
from typing import Dict

from fastapi import status

from misc.openapi_extra import err_response_doc

CONNECTION_TIMEOUT = int(timedelta(minutes=5).total_seconds())

TOGGLE_ERROR_RESPONSE: Dict = {
    status.HTTP_400_BAD_REQUEST: err_response_doc('When the datasource cannot be toggled'),
    status.HTTP_404_NOT_FOUND: err_response_doc('When the datasource does not exist')
}

NOT_ENABLED_RESPONSE: Dict = {
    status.HTTP_400_BAD_REQUEST: err_response_doc('When the datasource is not enabled')
}