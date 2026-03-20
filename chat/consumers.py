
import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from .models import Message
from accounts.models import User
from django.utils import timezone


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.user = self.scope["user"]
        self.other_user_id = self.scope['url_route']['kwargs']['user_id']
        self.room_name = f"{min(self.user.id, self.other_user_id)}_{max(self.user.id, self.other_user_id)}"
        self.room_group_name = f"chat_{self.room_name}"

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        # online
        await sync_to_async(User.objects.filter(id=self.user.id).update)(
            is_online=True
        )

        await self.channel_layer.group_send(
            self.room_group_name,
            {"type": "user_online", "user": self.user.username}
        )

    async def disconnect(self, close_code):
        await sync_to_async(User.objects.filter(id=self.user.id).update)(
            is_online=False,
            last_seen=timezone.now()
        )

        await self.channel_layer.group_send(
            self.room_group_name,
            {"type": "user_offline", "user": self.user.username}
        )

        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        msg_type = data.get("type")

        # MESSAGE
        if msg_type == "message":
            message = data.get("message")

            receiver = await sync_to_async(User.objects.get)(id=self.other_user_id)

            saved = await sync_to_async(Message.objects.create)(
                sender=self.user,
                receiver=receiver,
                content=message
            )

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat_message",
                    "message": message,
                    "sender": self.user.username,
                    "created_at": str(saved.created_at)
                }
            )

        # SEEN
        elif msg_type == "seen":
            await sync_to_async(
                Message.objects.filter(
                    sender_id=self.other_user_id,
                    receiver=self.user,
                    is_seen=False
                ).update
            )(is_seen=True)

            await self.channel_layer.group_send(
                self.room_group_name,
                {"type": "message_seen", "user": self.user.username}
            )

        # TYPING
        elif msg_type == "typing":
            await self.channel_layer.group_send(
                self.room_group_name,
                {"type": "user_typing", "user": self.user.username}
            )

            await asyncio.sleep(2)

            await self.channel_layer.group_send(
                self.room_group_name,
                {"type": "user_stop_typing", "user": self.user.username}
            )

    # SENDERS

    async def chat_message(self, event):
        await self.send(json.dumps({
            "type": "message",
            "message": event["message"],
            "sender": event["sender"],
            "created_at": event["created_at"]
        }))

    async def message_seen(self, event):
        await self.send(json.dumps({
            "type": "seen",
            "user": event["user"]
        }))

    async def user_typing(self, event):
        await self.send(json.dumps({
            "type": "typing",
            "user": event["user"]
        }))

    async def user_stop_typing(self, event):
        await self.send(json.dumps({
            "type": "stop_typing",
            "user": event["user"]
        }))

    async def user_online(self, event):
        await self.send(json.dumps({
            "type": "online",
            "user": event["user"]
        }))

    async def user_offline(self, event):
        await self.send(json.dumps({
            "type": "offline",
            "user": event["user"]
        }))
