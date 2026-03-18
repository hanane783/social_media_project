

from django.urls import path
from .views import (
    PostView,
    CommentView,
    TogglePostLikeView, 
    ToggleCommentLikeView,
    UpdatePostView,
    DeletePostView,
    UpdateCommentView, 
    DeleteCommentView,
    ToggleFollowView,
    CommentListView,
    PostListView,
    FeedView,
 
)

urlpatterns = [
    # ----------------- Post -----------------
    path('posts/', PostView.as_view(), name='posts'),  # GET كل البوستات / POST إنشاء بوست
    path('post/<int:post_id>/update/', UpdatePostView.as_view(), name='update-post'),
    path('post/<int:post_id>/delete/', DeletePostView.as_view(), name='delete-post'),
    path('posts/', PostListView.as_view()),

    # ----------------- Comment -----------------
    path('posts/<int:post_id>/comments/', CommentView.as_view(), name='comments'),  # GET/POST تعليقات بوست معين
    path('comment/<int:comment_id>/update/', UpdateCommentView.as_view(), name='update-comment'),
    path('comment/<int:comment_id>/delete/', DeleteCommentView.as_view(), name='delete-comment'),
    path('post/<int:post_id>/comments/', CommentListView.as_view()),
    # ----------------- Post Like ,Comment Like -----------------
    path('post/<int:post_id>/like/', TogglePostLikeView.as_view(), name='like-post'),
    path('comment/<int:comment_id>/like/', ToggleCommentLikeView.as_view(), name='like-comment'),

    # ----------------- Follow -----------------
    path('user/<int:user_id>/follow/', ToggleFollowView.as_view(), name='toggle-follow'),
    path('feed/', FeedView.as_view()),
]