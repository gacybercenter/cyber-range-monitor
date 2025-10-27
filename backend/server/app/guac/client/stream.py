import dataclasses as dc
from collections.abc import AsyncIterable, AsyncIterator

_LBRACE = ord('{')
_RBRACE = ord('}')
_QUOTE = ord('"')
_BSLASH = ord('\\')
_LBRACK = ord('[')
_RBRACK = ord(']')
_COMMA = ord(',')


@dc.dataclass(slots=True)
class JSONStreamReader:
    '''
    Simple JSON stream parser that yields complete JSON objects
    from an async byte stream for the history responses, since they
    return massive arrays (>5K objects)
    '''
    capturing: bool = False
    depth: int = 0
    in_string: bool = False
    escape: bool = False
    buffer: bytearray = dc.field(default_factory=bytearray)

    require_top_array: bool = True
    in_top_array: bool = False
    top_depth: int = 0  # track [] depth at top level

    def _start_capture(self, b: int) -> None:
        self.capturing = True
        self.depth = 1
        self.in_string = False
        self.escape = False
        self.buffer.clear()
        self.buffer.append(b)

    def _string_step(self, b: int) -> None:
        if self.escape:
            self.escape = False
        elif b == _BSLASH:
            self.escape = True
        elif b == _QUOTE:
            self.in_string = False

    def _capture_step(self, b: int) -> bool:
        self.buffer.append(b)
        if self.in_string:
            self._string_step(b)
            return False

        if b == _QUOTE:
            self.in_string = True
            return False

        if b == _LBRACE:
            self.depth += 1
            return False

        if b == _RBRACE:
            self.depth -= 1
            if self.depth == 0:
                self.capturing = False
                return True

        return False

    def reset(self) -> None:
        self.capturing = False
        self.depth = 0
        self.in_string = False
        self.escape = False
        self.buffer.clear()
        self.in_top_array = False
        self.top_depth = 0

    def checkbyte(self, b: int) -> None:
        if self.require_top_array and not self.in_top_array:
            if b == _LBRACK:
                self.top_depth += 1
                self.in_top_array = True
            return

        if self.require_top_array and self.in_top_array:
            if b == _RBRACK:
                self.top_depth -= 1
                if self.top_depth <= 0:
                    self.in_top_array = False
                return

            if b in (_COMMA, 9, 10, 13, 32):
                return

        if b == _LBRACE:
            self._start_capture(b)

    async def readbytes(self, byte_iter: AsyncIterable[bytes]) -> AsyncIterator[bytes]:
        try:
            async for chunk in byte_iter:
                for b in chunk:
                    if not self.capturing:
                        self.checkbyte(b)
                        continue

                    # capture mode
                    if self._capture_step(b):
                        yield bytes(self.buffer)

            if self.capturing:
                raise ValueError('Truncated JSON: stream ended mid-object')
        finally:
            self.reset()
