from typing import Generic, TypeVar

import msgspec

S = TypeVar('S', bound=msgspec.Struct)


class MsgspecStructCodec(Generic[S]):
    '''
    A codec for encoding and decoding msgspec.Struct
    objects.
    '''

    def __init__(self, struct_type: type[S]) -> None:
        self._encoder: msgspec.json.Encoder = msgspec.json.Encoder()
        self._decoder: msgspec.json.Decoder[S] = msgspec.json.Decoder(struct_type)

    def encode(self, obj: S) -> bytes:
        return self._encoder.encode(obj)

    def decode(self, raw: bytes) -> S | None:
        try:
            struct: S = self._decoder.decode(raw)
        except msgspec.DecodeError:
            return None
        return struct
