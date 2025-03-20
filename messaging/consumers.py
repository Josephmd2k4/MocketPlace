import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Message
from asgiref.sync import sync_to_async
from django.contrib.auth.models import User

class MessagingConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.current_user = self.scope['url_route']['kwargs']['current_user']
        self.target_user = self.scope['url_route']['kwargs']['target_user']
        users_sorted = sorted([self.current_user , self.target_user])
        self.room_group_name = f"chat_{users_sorted[0]}_{users_sorted[1]}"

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    @sync_to_async
    def save_message(self, message_text, sender, receiver):
        # Get User instances for sender and receiver
        sender_user = User.objects.get(username=sender)
        receiver_user = User.objects.get(username=receiver)

        # Save the incoming message to the database
        message = Message.objects.create(
            content=message_text,
            sender=sender_user,  # Use the User instance here
            receiver=receiver_user  # Use the User instance here
        )
        return message

    async def receive(self, text_data):
        print("Received data:", text_data)
        try:
            text_data_json = json.loads(text_data)
            message = text_data_json["message"]
            username = text_data_json["username"]
            target_username = text_data_json.get("target_username")  # Use `.get()` to avoid KeyError

            if not target_username:
                print("Warning: Missing target_username in message payload")

            # Send message to room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat_message",
                    "message": message,
                    "username": username,
                    "target_username": target_username
                }
            )
            saved_message = await self.save_message(message, username, target_username)
        except json.JSONDecodeError:
            print("Error: Received invalid JSON data")

    async def chat_message(self, event):
        message = event["message"]
        username = event["username"]

        await self.send(text_data=json.dumps({
            "message": message,
            "username": username,
        }))
