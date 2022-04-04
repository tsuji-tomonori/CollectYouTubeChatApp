from __future__ import annotations

import gzip
import json
import logging
import os

from apis import get_chat_data, get_chat_id
from aws_resource import S3, Sns, Sqs, Ssm
from sqs_if import SqsIo

# set logging
logger = logging.getLogger()
logger.setLevel(os.environ["LOG_LEVEL"])


def build_file_path(channel_id: str, video_id: str, etag: str) -> str:
    return f"{channel_id}/{video_id}/{etag}.json.gz"


def service(event: dict, env: dict):
    logger.debug("Service Start!")
    ssm = Ssm()
    s3 = S3()
    sqs = Sqs()
    sns = Sns()

    youtube_api_key = ssm.value(env["YOUTUBE_API_KEY"])

    for record in event["Records"]:

        if "Sns" in record.keys():
            # SNS の場合
            message = json.loads(record["Sns"]["Message"])
        else:
            # SQS の場合
            message = json.loads(record["body"])

        logger.debug(json.dumps(message, indent=2))
        video_id = message["video_id"]
        channel_id = message["channel_id"]
        title = message["title"]

        if "chat_id" in message.keys():
            # SQS の場合
            chat_id = message["chat_id"]
        else:
            # SNS の場合
            chat_id = get_chat_id(youtube_api_key, video_id)

        page_token = message.get("page_token", None)
        chat_data = get_chat_data(youtube_api_key, chat_id, page_token)

        if "nextPageToken" in chat_data.keys():
            # 何かしら取得できた場合
            file_path = build_file_path(
                channel_id,
                video_id,
                chat_data["etag"]
            )
            s3.upload(
                data=gzip.compress(json.dumps(
                    chat_data, ensure_ascii=False).encode()),
                bucket_name=env["bucket_name"],
                file_path=file_path,
                tags={
                    "channel_id": channel_id,
                    "video_id": video_id,
                    "creater": "sdk",
                    "project": "CollectYouTubeChatApp",
                }
            )
            sqs.send(
                queue_url=env["que_url"],
                message=SqsIo(
                    chat_id=chat_id,
                    page_token=chat_data["nextPageToken"],
                    video_id=video_id,
                    channel_id=channel_id,
                    title=title
                ).json(),
                delay_sec=20,
            )
            logger.info(f"[{video_id}] s3 upload at {file_path}")
        else:
            # 取得が終了した場合
            sns.publish(
                topick_arn=env["topic_arn"],
                message=f"チャット欄取得が完了しました!\n{title}",
                subject="チャット欄取得完了通知"
            )
            logger.info(f"[{video_id}] fin collection")


def handler(event, context):
    try:
        service(
            event=event,
            env={
                "YOUTUBE_API_KEY": os.environ["YOUTUBE_API_KEY"],
                "bucket_name": os.environ["BUCKET_NAME"],
                "que_url": os.environ["QUE_URL"],
                "topic_arn": os.environ["TOPIC_ARN"]
            },
        )
        return {
            "status_code": 200
        }
    except Exception as e:
        logging.exception(f"event={json.dumps(event, indent=2)}")
        sns = Sns()
        sns.publish(
            topick_arn=os.environ["TOPIC_ARN"],
            message=f"チャット欄取得に失敗しました\n{e}",
            subject="チャット欄取得エラー通知"
        )
        return {
            "status_code": 400
        }
