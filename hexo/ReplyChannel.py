import json
from channels import Channel

class ReplyChannel():
    def __init__(self, channel_id):
        self.reply_channel = Channel(channel_id)
    
    def send(self, data):
        """
        wraps the default send method with serialization
        """
        if isinstance(data, str):
            self.reply_channel.send({
                "text": data
            })
        else:
            self.reply_channel.send({
                "text": json.dumps(data)
            })


