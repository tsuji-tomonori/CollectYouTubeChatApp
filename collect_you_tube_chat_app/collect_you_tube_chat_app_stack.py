import aws_cdk as cdk
from aws_cdk import Stack
from aws_cdk import aws_iam as iam
from aws_cdk import aws_lambda as _lambda
from aws_cdk import aws_logs as logs
from aws_cdk import aws_s3 as s3
from aws_cdk import aws_sns as sns
from aws_cdk import aws_sqs as sqs
from aws_cdk import aws_ssm as ssm
from aws_cdk.aws_lambda_event_sources import SqsEventSource
from constructs import Construct

PROJECK_NAME = "CollectYouTubeChatApp"
DESCRIPTION = "Collect YouTube Chat Messages"


def build_resource_name(resource_name: str, service_name: str) -> str:
    return f"{resource_name}_{service_name}_cdk"


class CollectYouTubeChatAppStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        role = iam.Role(
            self, build_resource_name("rol", "collect_youtube_chat_role"),
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "service-role/AWSLambdaBasicExecutionRole")
            ],
            role_name=build_resource_name(
                "rol", "collect_youtube_chat_role"),
            description=DESCRIPTION
        )
        cdk.Tags.of(role).add("service_name", build_resource_name(
            "rol", "collect_youtube_chat_role"))

        layer = _lambda.LayerVersion(
            self, build_resource_name("lyr", "request"),
            code=_lambda.Code.from_asset("layer"),
            layer_version_name=build_resource_name("lyr", "request"),
            compatible_runtimes=[_lambda.Runtime.PYTHON_3_9],
            description="Python lib: request",
        )

        fn = _lambda.Function(
            self, build_resource_name("lmd", "collect_youtube_chat_service"),
            code=_lambda.Code.from_asset("lambda"),
            handler="lambda_function.handler",
            runtime=_lambda.Runtime.PYTHON_3_9,
            function_name=build_resource_name(
                "lmd", "collect_youtube_chat_service"),
            environment={
                "LOG_LEVEL": "INFO",
            },
            description=DESCRIPTION,
            timeout=cdk.Duration.seconds(300),
            memory_size=256,
            role=role,
            log_retention=logs.RetentionDays.THREE_MONTHS,
            layers=[layer]
        )
        cdk.Tags.of(role).add("service_name", build_resource_name(
            "lmd", "collect_youtube_chat_service"))

        bucket = s3.Bucket(
            self, "s3s-collect-youtube-chat-bucket-cdk",
            bucket_name="s3s-collect-youtube-chat-bucket-cdk",
        )
        bucket.grant_put(role)
        cdk.Tags.of(role).add("service_name",
                              "s3s-collect-youtube-chat-bucket-cdk")
        fn.add_environment(
            key="BUCKET_NAME",
            value=bucket.bucket_name
        )

        queue = sqs.Queue(
            self, build_resource_name("sqs", "collect_youtube_chat_queue"),
            queue_name=build_resource_name(
                "sqs", "collect_youtube_chat_queue"),
            visibility_timeout=cdk.Duration.seconds(500)
        )
        queue.grant_send_messages(role)
        cdk.Tags.of(role).add("service_name", build_resource_name(
            "sqs", "collect_youtube_chat_queue"))
        fn.add_environment(
            key="QUE_URL",
            value=queue.queue_url
        )
        sqs_event = SqsEventSource(queue)
        fn.add_event_source(sqs_event)

        topic = sns.Topic(
            self, build_resource_name("sns", "collect_youtube_chat_topic"),
            topic_name=build_resource_name(
                "sns", "collect_youtube_chat_topic"),
        )
        topic.grant_publish(role)
        cdk.Tags.of(role).add("service_name", build_resource_name(
            "sns", "collect_youtube_chat_topic"))
        fn.add_environment(
            key="TOPIC_ARN",
            value=topic.topic_arn
        )

        collect_youtube_api_key = ssm.StringParameter.from_secure_string_parameter_attributes(
            self, "collect_youtube_api_key",
            version=1,
            parameter_name="collect_youtube_api_key",
        )
        collect_youtube_api_key.grant_read(role)
        fn.add_environment(
            key="YOUTUBE_API_KEY",
            value=collect_youtube_api_key.parameter_name,
        )

        for resource in [role, fn, bucket, queue, topic]:
            cdk.Tags.of(resource).add("project", PROJECK_NAME)
            cdk.Tags.of(resource).add("creater", "cdk")
