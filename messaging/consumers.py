import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Message
from asgiref.sync import sync_to_async
from django.contrib.auth.models import User
from notifications.models import Notification
from notifications.views import send_dm_notification
from django.contrib.contenttypes.models import ContentType
import datetime
from django.utils.timesince import timesince
from dateutil import parser

class MessagingConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.current_user = self.scope['url_route']['kwargs']['current_user']
        self.target_user = self.scope['url_route']['kwargs']['target_user']
        users_sorted = sorted([self.current_user, self.target_user])
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
    def save_message(self, message_text, sender, receiver, timestamp):
        sender_user = User.objects.get(username=sender)
        receiver_user = User.objects.get(username=receiver)

        message = Message.objects.create(
            content=message_text,
            sender=sender_user,
            receiver=receiver_user,
            timestamp=timestamp
        )

        return message

    async def receive(self, text_data):
        print("Received data:", text_data)
        try:
            text_data_json = json.loads(text_data)
            message = text_data_json["message"]
            username = text_data_json["username"]
            target_username = text_data_json.get("target_username")
            timestamp = text_data_json["timestamp"]  # Get the raw timestamp as string
            timestamp = parser.parse(timestamp)  # Parse it into a datetime object
            if not target_username:
                print("Warning: Missing target_username in message payload")


            # Save the message without creating the notification here
            saved_message = await self.save_message(message, username, target_username, timestamp)

            
            # Send the message to the room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat_message",
                    "message": message,
                    "username": username,
                    "target_username": target_username,
                    "timestamp": timestamp  # Send timestamp as ISO string
                }
            )

            # Handle notifications (if needed)
            await sync_to_async(send_dm_notification)(
                username, target_username, message_id=saved_message.id
            )

        except Exception as e:
            print("Error receiving message:", e)

    async def chat_message(self, event):
        message = event["message"]
        username = event["username"]
        timestamp = event["timestamp"]

        # Ensure timestamp is a datetime object for correct formatting
        if isinstance(timestamp, str):
            timestamp = parser.parse(timestamp)

        # Calculate time difference using timesince
        time_diff = timesince(timestamp)
        time_diff = time_diff.split(',')[0]  # Only use the largest unit of time

        # Send the message with formatted timestamp to the WebSocket
        await self.send(text_data=json.dumps({
            "message": message,
            "username": username,
            "timestamp": "Just Now",
        }))
