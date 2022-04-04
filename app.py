#!/usr/bin/env python3
import os

import aws_cdk as cdk

from collect_you_tube_chat_app.collect_you_tube_chat_app_stack import CollectYouTubeChatAppStack


app = cdk.App()
CollectYouTubeChatAppStack(
    app, "CollectYouTubeChatAppStack", stack_name="CollectYouTubeChatAppStack")

app.synth()
