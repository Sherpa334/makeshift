import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
import time


chat_history = []
connected_users = {}

class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.room_group_name = 'test'
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        self.accept()
        username = self.scope['user'].username
        connected_users[username] = time.time()
        self.send_user_list()
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
    def disconnect(self, close_code):
        username = self.scope['user'].username
        del connected_users[username]
        self.send_user_list()
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        if text_data_json.get('type') == 'get_user_list':
            self.get_user_list(None)
        else:
            message = text_data_json['message']
            message = message.replace("&", "&amp;")
            message = message.replace("<", "&lt;")
            message = message.replace(">", "&gt;")
            username = text_data_json.get('username', 'Guest')
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
    
    def send_user_list(self):
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'user_list',
                'users': [
                    {'username': username, 'connection_time': int(connected_users[username])}
                    for username in connected_users
                ],
            }
        )

    def user_list(self, event):
        self.send(text_data=json.dumps({
            'type': 'user_list',
            'users': event['users'],
        }))
    def get_user_list(self, event):
        self.send_user_list()