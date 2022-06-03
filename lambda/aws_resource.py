import json

import boto3


class AwsResource:
    def __init__(self, profile: str = None):
        if profile is not None:
            self.session = boto3.Session(profile_name=profile)
        else:
            self.session = boto3.Session()


class S3(AwsResource):
    def __init__(self, profile: str = None):
        super().__init__(profile)
        self.client = self.session.client("s3")

    def upload(self, data: bin, bucket_name: str, file_path: str) -> None:
        self.client.put_object(
            Body=data,
            Bucket=bucket_name,
            Key=file_path,
        )

    def _tag_strf_query_paramater(self, tags: dict) -> str:
        return "&".join(f"{k}={v}" for k, v in tags.items())


class Ssm(AwsResource):
    def __init__(self, profile: str = None):
        super().__init__(profile)
        self.client = self.session.client("ssm")

    def value(self, key: str):
        value = self.client.get_parameter(
            Name=key,
            WithDecryption=True
        )
        return value["Parameter"]["Value"]


class Sqs(AwsResource):
    def __init__(self, profile: str = None):
        super().__init__(profile)
        self.client = self.session.client("sqs")

    def send(self, queue_url: str, message: dict, delay_sec: int) -> None:
        self.client.send_message(
            QueueUrl=queue_url,
            MessageBody=json.dumps(message),
            DelaySeconds=delay_sec
        )


class Sns(AwsResource):
    def __init__(self, profile: str = None):
        super().__init__(profile)
        self.client = self.session.client("sns")

    def publish(self, topick_arn: str, message: str, subject: str) -> None:
        self.client.publish(
            TopicArn=topick_arn,
            Message=message,
            Subject=subject
        )
