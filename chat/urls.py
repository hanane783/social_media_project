
from django.urls import path
from .views import ChatHistoryView, ConversationsView

urlpatterns = [
    path('chat/<int:user_id>/', ChatHistoryView.as_view(), name='chat-history'),
    path('conversations/', ConversationsView.as_view(), name='conversations'),
]