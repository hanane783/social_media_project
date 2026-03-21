

from django.urls import path
from .views import (
    PostView, CommentView, TogglePostLikeView, ToggleCommentLikeView,
    UpdatePostView, DeletePostView, UpdateCommentView, DeleteCommentView,
    ToggleFollowView, CommentListView, PostListView, FeedView, SharePostView,
    toggle_save_post, SavedPostsView, FollowersView, FollowingView, SuggestionsView,
    reply_comment, react_comment,
)

urlpatterns = [
    # ----------------- Post -----------------
    path('posts/', PostView.as_view(), name='posts'),
    path('post/<int:post_id>/update/', UpdatePostView.as_view(), name='update-post'),
    path('post/<int:post_id>/delete/', DeletePostView.as_view(), name='delete-post'),
    path('posts/list/', PostListView.as_view(), name='list-posts'),
    path('share/<int:post_id>/', SharePostView.as_view(), name='share-post'),

    # ----------------- Comment -----------------
    path('posts/<int:post_id>/comments/', CommentView.as_view(), name='comments'),
    path('comment/<int:comment_id>/update/', UpdateCommentView.as_view(), name='update-comment'),
    path('comment/<int:comment_id>/delete/', DeleteCommentView.as_view(), name='delete-comment'),
    path('post/<int:post_id>/comments/list/', CommentListView.as_view(), name='list-comments'),
    path('comment/<int:comment_id>/reply/', reply_comment),
    path('comment/<int:comment_id>/react/', react_comment),

    # ----------------- Like -----------------
    path('post/<int:post_id>/like/', TogglePostLikeView.as_view(), name='like-post'),
    path('comment/<int:comment_id>/like/', ToggleCommentLikeView.as_view(), name='like-comment'),
    path('post/<int:post_id>/save/', toggle_save_post),
    path('saved-posts/', SavedPostsView.as_view()),

    # ----------------- Follow -----------------
    path('user/<int:user_id>/follow/', ToggleFollowView.as_view(), name='toggle-follow'),
    path('user/<int:user_id>/followers/', FollowersView.as_view()),
    path('user/<int:user_id>/following/', FollowingView.as_view()),
    path('suggestions/', SuggestionsView.as_view()),
    path('feed/', FeedView.as_view()),
]