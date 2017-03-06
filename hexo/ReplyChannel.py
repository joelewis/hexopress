import json
from channels import Channel

class ReplyChannel():
    def __init__(self, channel_id):
        self.reply_channel = Channel(channel_id)
    
    def send(self, event, data):
        """
        wraps the default send method with serialization
        """
        response = {
            "event": event,
            "data": data
        }
        self.reply_channel.send({
            "text": json.dumps(response)
        })


