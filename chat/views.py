from django.shortcuts import render
from rest_framework.views import APIView

from rest_framework.response import Response
from rest_framework import permissions, status
from drf_spectacular.utils import extend_schema
from django.shortcuts import get_object_or_404

from rest_framework.permissions import IsAuthenticated
# Create your views here.
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
                "created_at": m.created_at
            })

        return Response(data)