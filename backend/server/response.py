from typing import Any

import msgspec
from fastapi.responses import JSONResponse

from server.schema import PydanticModel


class MsgspecJsonResponse(JSONResponse):
    '''
    improves performance of the JSONResponse by using msgspec to serialize the data
    '''

    media_type = 'application/json'

    def render(self, content: Any) -> bytes:
        if isinstance(content, bytes):
            return content

        if isinstance(content, PydanticModel):
            return content.serialize()

        return msgspec.json.encode(content)
