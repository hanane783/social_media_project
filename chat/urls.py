from django.urls import path
from .views import  ChatHistoryView

urlpatterns = [


path('chat/<int:user_id>/', ChatHistoryView.as_view(),name='history'),
]