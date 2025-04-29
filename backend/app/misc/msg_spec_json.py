from typing import Any
import msgspec

from fastapi.responses import JSONResponse



class MsgSpecJSONResponse(JSONResponse):
    '''improves performance of the JSONResponse by using msgspec to serialize the data'''

    def render(self, content: Any) -> bytes:
        """Renders the content using msgspec.json"""
        return msgspec.json.encode(content)
