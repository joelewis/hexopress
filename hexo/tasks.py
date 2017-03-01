from __future__ import absolute_import
import time
import json
import logging

from hexopress.celery import app
from hexo.ReplyChannel import ReplyChannel

@app.task
def respond_in_three(user_id, channel_id, message):
    print message
    reply_channel = ReplyChannel(channel_id)
    time.sleep(1)
    reply_channel.send("slept for 1 sec")
    time.sleep(3)
    reply_channel.send("slept for 3 sec")
    reply_channel.send(message)