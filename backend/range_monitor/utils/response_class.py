from typing import Any

import msgspec
from fastapi.responses import JSONResponse


class MsgspecJsonResponse(JSONResponse):
    """
    improves performance of the JSONResponse by using msgspec to serialize the data
    """

    def render(self, content: Any) -> bytes:
        return msgspec.json.encode(content)
