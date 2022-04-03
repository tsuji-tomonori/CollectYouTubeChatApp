import aws_cdk as core
import aws_cdk.assertions as assertions

from collect_you_tube_chat_app.collect_you_tube_chat_app_stack import CollectYouTubeChatAppStack

# example tests. To run these tests, uncomment this file along with the example
# resource in collect_you_tube_chat_app/collect_you_tube_chat_app_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = CollectYouTubeChatAppStack(app, "collect-you-tube-chat-app")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
