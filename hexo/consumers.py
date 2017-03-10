import json
from channels.auth import channel_session_user, channel_session_user_from_http
from hexo import tasks
from hexo.ReplyChannel import ReplyChannel

@channel_session_user
def ws_message(message):
    if not message.user.is_authenticated():
        return message.reply_channel.send({
            "text": json.dumps({"error": "user not authenticated"})
        })

    data = json.loads(message["text"])
    try:
        task = getattr(tasks, data["task"])
    except:
        message.reply_channel.send({'text': {'event': 'task not found'}})
        return 
    reply_channel = ReplyChannel(message.reply_channel.name)
    task.delay(message.user.id, message.reply_channel.name, data["data"])

@channel_session_user_from_http
def ws_connect(message):
    message.reply_channel.send({
        "text": json.dumps({"response": "connected -->" + message.reply_channel.name})
    })