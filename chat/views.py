# from django.shortcuts import render
# from rest_framework.views import APIView

# from rest_framework.response import Response
# from rest_framework import permissions, status
# from drf_spectacular.utils import extend_schema
# from django.shortcuts import get_object_or_404

# from django.db.models import Q
# from drf_spectacular.utils import extend_schema
# from rest_framework.permissions import IsAuthenticated





# @extend_schema(
#     description="Get user conversations with last message and unread count",
#     responses={
#         200: {
#             "type": "array",
#             "items": {
#                 "type": "object",
#                 "properties": {
#                     "user_id": {"type": "integer"},
#                     "username": {"type": "string"},
#                     "last_message": {"type": "string"},
#                     "time": {"type": "string"},
#                     "unread_count": {"type": "integer"},
#                     "file": {"type": "string", "nullable": True}
#                 }
#             }
#         }
#     }
# )
# class ConversationsView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         user = request.user

#         conversations = Message.objects.filter(
#             Q(sender=user) | Q(receiver=user)
#         ).order_by('-timestamp')

#         search = request.GET.get('search', '')
#         if search:
#             conversations = conversations.filter(
#                 Q(senderusernameicontains=search) |
#                 Q(receiverusernameicontains=search)
#             )

#         users = {}
#         data = []

#         for msg in conversations:
#             other_user = msg.receiver if msg.sender == user else msg.sender

#             if other_user.id not in users:
#                 users[other_user.id] = True

#                 unread_count = Message.objects.filter(
#                     sender=other_user,
#                     receiver=user,
#                     is_seen=False
#                 ).count()

#                 data.append({
#                     "user_id": other_user.id,
#                     "username": other_user.username,
#                     "last_message": msg.content,
#                     "time": msg.timestamp,
#                     "unread_count": unread_count,
#                     "file": msg.file.url if msg.file else None
#                 })

#         return Response(data)

# @extend_schema(
#     description="Get chat history between current user and another user",
#     responses={
#         200: {
#             "type": "array",
#             "items": {
#                 "type": "object",
#                 "properties": {
#                     "sender": {"type": "string"},
#                     "content": {"type": "string"},
#                     "is_seen": {"type": "boolean"},
#                     "file": {"type": "string", "nullable": True},
#                     "created_at": {"type": "string"}
#                 }
#             }
#         }
#     }
# )
# class ChatHistoryView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request, user_id):
#         messages = Message.objects.filter(
#             sender__in=[request.user.id, user_id],
#             receiver__in=[request.user.id, user_id]
        
#         ).order_by('created_at')

#         data = []
#         for m in messages:
#             data.append({
#                 "sender": m.sender.username,
#                 "content": m.content,
#                 "is_seen": m.is_seen,
#                 "file": m.file.url if m.file else None,
#                 "created_at": m.created_at
#             })

# -------------------------- Conversations --------------------------
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from django.db.models import Q
from .models import Message

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

        conversations = Message.objects.filter(
            Q(sender=user) | Q(receiver=user)
        ).order_by('-created_at')

        search = request.GET.get('search', '')

        if search:
            conversations = conversations.filter(
                Q(sender__username__icontains=search) |
                Q(receiver__username__icontains=search)
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

        # -------------------------- Chat History --------------------------
@extend_schema(
    description="Get chat history between current user and another user",
    responses={
        200: {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "sender": {"type": "string"},
                    "content": {"type": "string"},
                    "is_seen": {"type": "boolean"},
                    "file": {"type": "string", "nullable": True},
                    "created_at": {"type": "string"}
                }
            }
        }
    }
)
class ChatHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        messages = Message.objects.filter(
            sender__in=[request.user.id, user_id],
            receiver__in=[request.user.id, user_id]
        ).order_by('created_at')

        data = []
        for m in messages:
            data.append({
                "sender": m.sender.username,
                "content": m.content,
                "is_seen": m.is_seen,
                "file": m.file.url if m.file else None,
                "created_at": m.created_at
            })
        return Response(data)