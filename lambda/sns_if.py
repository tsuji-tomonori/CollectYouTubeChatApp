from typing import NamedTuple
import json


class SnsIoTuple(NamedTuple):
    video_id: str
    channel_id: str
    title: str


class SnsIo(SnsIoTuple):
    def message(self) -> str:
        return json.dumps(self._asdict(), ensure_ascii=False)
