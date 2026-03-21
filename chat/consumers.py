
# import json
# import asyncio
# from channels.generic.websocket import AsyncWebsocketConsumer
# from asgiref.sync import sync_to_async
# from .models import Message
# from accounts.models import User
# from django.utils import timezone


# class ChatConsumer(AsyncWebsocketConsumer):

#     async def connect(self):
#         self.user = self.scope["user"]
#         self.other_user_id = self.scope['url_route']['kwargs']['user_id']
#         self.room_name = f"{min(self.user.id, self.other_user_id)}_{max(self.user.id, self.other_user_id)}"
#         self.room_group_name = f"chat_{self.room_name}"

#         await self.channel_layer.group_add(self.room_group_name, self.channel_name)
#         await self.accept()

#         # online
#         await sync_to_async(User.objects.filter(id=self.user.id).update)(
#             is_online=True
#         )

#         await self.channel_layer.group_send(
#             self.room_group_name,
#             {"type": "user_online", "user": self.user.username}
#         )

#     async def disconnect(self, close_code):
#         await sync_to_async(User.objects.filter(id=self.user.id).update)(
#             is_online=False,
#             last_seen=timezone.now()
#         )

#         await self.channel_layer.group_send(
#             self.room_group_name,
#             {"type": "user_offline", "user": self.user.username}
#         )

#         await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

#     async def receive(self, text_data):
#         data = json.loads(text_data)
#         msg_type = data.get("type")

#         # MESSAGE
#         if msg_type == "message":
#             message = data.get("message")

#             receiver = await sync_to_async(User.objects.get)(id=self.other_user_id)

#             saved = await sync_to_async(Message.objects.create)(
#                 sender=self.user,
#                 receiver=receiver,
#                 content=message
#             )

#             await self.channel_layer.group_send(
#                 self.room_group_name,
#                 {
#                     "type": "chat_message",
#                     "message": message,
#                     "sender": self.user.username,
#                     "created_at": str(saved.created_at)
#                 }
#             )

#         # SEEN
#         elif msg_type == "seen":
#             await sync_to_async(
#                 Message.objects.filter(
#                     sender_id=self.other_user_id,
#                     receiver=self.user,
#                     is_seen=False
#                 ).update
#             )(is_seen=True)

#             await self.channel_layer.group_send(
#                 self.room_group_name,
#                 {"type": "message_seen", "user": self.user.username}
#             )

#         # TYPING
#         elif msg_type == "typing":
#             await self.channel_layer.group_send(
#                 self.room_group_name,
#                 {"type": "user_typing", "user": self.user.username}
#             )

#             await asyncio.sleep(2)

#             await self.channel_layer.group_send(
#                 self.room_group_name,
#                 {"type": "user_stop_typing", "user": self.user.username}
#             )

#     # SENDERS

#     async def chat_message(self, event):
#         await self.send(json.dumps({
#             "type": "message",
#             "message": event["message"],
#             "sender": event["sender"],
#             "created_at": event["created_at"]
#         }))

#     async def message_seen(self, event):
#         await self.send(json.dumps({
#             "type": "seen",
#             "user": event["user"]
#         }))

#     async def user_typing(self, event):
#         await self.send(json.dumps({
#             "type": "typing",
#             "user": event["user"]
#         }))

#     async def user_stop_typing(self, event):
#         await self.send(json.dumps({
#             "type": "stop_typing",
#             "user": event["user"]
#         }))

#     async def user_online(self, event):
#         await self.send(json.dumps({
#             "type": "online",
#             "user": event["user"]
#         }))

#     async def user_offline(self, event):
#         await self.send(json.dumps({
#             "type": "offline",
#             "user": event["user"]
#         }))


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

        # إنشاء اسم الغرفة حسب ترتيب IDs لتفادي تكرار الغرف
        self.room_name = f"{min(self.user.id, self.other_user_id)}_{max(self.user.id, self.other_user_id)}"
        self.room_group_name = f"chat_{self.room_name}"

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        # تعيين المستخدم أونلاين
        await sync_to_async(User.objects.filter(id=self.user.id).update)(
            is_online=True
        )

        # إخطار الغرفة أن المستخدم أصبح أونلاين
        await self.channel_layer.group_send(
            self.room_group_name,
            {"type": "user_online", "user": self.user.username}
        )

    async def disconnect(self, close_code):
        # تعيين المستخدم أوفلاين
        await sync_to_async(User.objects.filter(id=self.user.id).update)(
            is_online=False,
            last_seen=timezone.now()
        )
        # إخطار الغرفة أن المستخدم أصبح أوفلاين
        await self.channel_layer.group_send(
            self.room_group_name,
            {"type": "user_offline", "user": self.user.username}
        )
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        msg_type = data.get("type")

        if msg_type == "message":
            # إرسال رسالة
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
        elif msg_type == "seen":
            # وضع الرسائل كمقروءة
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
        elif msg_type == "typing":
            # إشعار كتابة
            await self.channel_layer.group_send(
                self.room_group_name,
                {"type": "user_typing", "user": self.user.username}
            )
            await asyncio.sleep(2)
            await self.channel_layer.group_send(
                self.room_group_name,
                {"type": "user_stop_typing", "user": self.user.username}
            )

    # -------------------- SENDERS --------------------
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
chat/views.py
نسخ التعليمات البرمجية
Python id="1c8nsd"
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from django.db.models import Q
from .models import Message
from accounts.models import User

# -------------------------- Conversations --------------------------
@extend_schema(
    description="Get user conversations with last message and unread count",
    responses={
        200: {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "user_id": {"type": "integer"},
                    "username": {"type": "string"},
                    "last_message": {"type": "string"},
                    "time": {"type": "string"},
                    "unread_count": {"type": "integer"},
                    "file": {"type": "string", "nullable": True}
                }
            }
        }
    }
)
class ConversationsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        conversations = Message.objects.filter(Q(sender=user) | Q(receiver=user)).order_by('-created_at')

        search = request.GET.get('search', '')
        if search:
            conversations = conversations.filter(
                Q(senderusernameicontains=search) |
                Q(receiverusernameicontains=search)
            )

        users = {}
        data = []
        for msg in conversations:
            other_user = msg.receiver if msg.sender == user else msg.sender
            if other_user.id not in users:
                users[other_user.id] = True
                unread_count = Message.objects.filter(
                    sender=other_user,
                    receiver=user,
                    is_seen=False
                ).count()
                data.append({
                    "user_id": other_user.id,
                    "username": other_user.username,
                    "last_message": msg.content,
                    "time": msg.created_at,
                    "unread_count": unread_count,
                    "file": msg.file.url if msg.file else None
                })
        return Response(data)
        
        await self.channel_layer.group_send(
                self.room_group_name,
                {"type": "message_seen", "user": self.user.username}
            )
        elif msg_type == "typing":
            # إشعار كتابة
            await self.channel_layer.group_send(
                self.room_group_name,
                {"type": "user_typing", "user": self.user.username}
            )
            await asyncio.sleep(2)
            await self.channel_layer.group_send(
                self.room_group_name,
                {"type": "user_stop_typing", "user": self.user.username}
            )

    # -------------------- SENDERS --------------------
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