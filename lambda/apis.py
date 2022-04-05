import requests
import logging
import json

# set logging
logger = logging.getLogger()


def get_chat_id(YT_API_KEY: str, video_id: str, kwags: dict = None) -> str:
    url = "https://www.googleapis.com/youtube/v3/videos"
    params = {
        "key": YT_API_KEY,
        "id": video_id,
        "part": "liveStreamingDetails"}
    if kwags is not None:
        params.update(kwags)
    data = requests.get(url, params=params).json()
    logger.debug(data)
    if len(data["items"]) == 0:
        raise IndexError(
            f"list index 0. data is {json.dumps(data, indent=2)}")
    return data["items"][0]["liveStreamingDetails"]["activeLiveChatId"]


def get_chat_data(YT_API_KEY, chat_id, page_token=None, kwags=None):
    url = "https://www.googleapis.com/youtube/v3/liveChat/messages"
    params = {
        'key': YT_API_KEY,
        'liveChatId': chat_id,
        'part': 'id,snippet,authorDetails'}
    if page_token is not None:
        params["pageToken"] = page_token
    if kwags is not None:
        params.update(kwags)
    data = requests.get(url, params=params).json()
    return data
