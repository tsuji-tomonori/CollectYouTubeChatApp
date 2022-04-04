from typing import NamedTuple


class SqsIoTuple(NamedTuple):
    chat_id: str
    page_token: str
    video_id: str
    channel_id: str
    title: str


class SqsIo(SqsIoTuple):
    def json(self) -> dict:
        return self._asdict()
