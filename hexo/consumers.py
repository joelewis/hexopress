import json
from channels.auth import channel_session_user, channel_session_user_from_http
from hexo import tasks
from hexo.ReplyChannel import ReplyChannel

@channel_session_user
def ws_message(message):
    data = json.loads(message["text"])
    try:
        task = getattr(tasks, data["task"])
    except:
        message.reply_channel.send({'text': 'task not found'})
        return 
    reply_channel = ReplyChannel(message.reply_channel.name)
    reply_channel.send("about to sleep")
    task.delay(message.user.id, message.reply_channel.name, data)

@channel_session_user_from_http
def ws_connect(message):
    message.reply_channel.send({
        "text": "connected -->" + message.reply_channel.name
    })