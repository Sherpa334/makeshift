import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync

chat_history = []

class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.room_group_name = 'test'
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        self.accept()

        for message in chat_history:
            self.send(text_data=json.dumps({
                'type': 'chat',
                'message': message['message'],
                'username': message['username'],
            }))

        self.send(text_data=json.dumps({
            'type': 'connection_established',
            'message': 'You are now connected!'
        }))

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        message = message.replace("&","&amp;")
        message = message.replace("<","&lt;")
        message = message.replace(">","&gt;")
        username = text_data_json.get('username', 'Guest')  # Use 'Guest' if username is not provided

        chat_history.append({
            'message': message,
            'username': username,
        })
        
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'username': username,
            }
        )

    def chat_message(self, event):
        message = event['message']
        username = event['username']
        self.send(text_data=json.dumps({
            'type': 'chat',
            'message': message,
            'username': username,
        }))