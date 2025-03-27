import json
import base64
import os
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.utils.timesince import timesince
from dateutil import parser
from .models import Message
from notifications.views import send_dm_notification

class MessagingConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.current_user = self.scope['url_route']['kwargs']['current_user']
        self.target_user = self.scope['url_route']['kwargs']['target_user']
        users_sorted = sorted([self.current_user, self.target_user])
        self.room_group_name = f"chat_{users_sorted[0]}_{users_sorted[1]}"

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    @sync_to_async
    def save_message(self, message_text, sender, receiver, timestamp, media_url):
        sender_user = User.objects.get(username=sender)
        receiver_user = User.objects.get(username=receiver)

        message = Message(sender=sender_user, receiver=receiver_user, content=message_text, timestamp=timestamp)
        if media_url:
            message.media = media_url
        message.save()
        return message

    async def receive(self, text_data):
        print("Received data:", text_data)
        try:
            text_data_json = json.loads(text_data)
            message = text_data_json.get("message", "")
            username = text_data_json["username"]
            target_username = text_data_json.get("target_username")
            media = text_data_json.get("media_url") 
            timestamp = parser.parse(text_data_json["timestamp"])

            if not target_username:
                print("Warning: Missing target_username in message payload")

            saved_message = await self.save_message(message, username, target_username, timestamp, media)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat_message",
                    "message": message,
                    "username": username,
                    "target_username": target_username,
                    "timestamp": str(timestamp),
                    "media": saved_message.media if saved_message.media else None,
                }
            )

            await sync_to_async(send_dm_notification)(
                username, target_username, message_id=saved_message.id
            )

        except Exception as e:
            print("Error receiving message:", e)

    async def chat_message(self, event):
        message = event["message"]
        username = event["username"]
        timestamp = event["timestamp"]
        media_url = event.get("media")

        if isinstance(timestamp, str):
            timestamp = parser.parse(timestamp)
        
        await self.send(text_data=json.dumps({
            "message": message,
            "username": username,
            "timestamp": "Just Now",
            "media": media_url,
        }))
