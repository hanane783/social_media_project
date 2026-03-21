from django.shortcuts import render

# # # Create your views here.
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from drf_spectacular.utils import extend_schema,OpenApiResponse
from django.shortcuts import get_object_or_404
from .models import Post, Comment, Like, CommentLike, Follow
from accounts.models import User
from rest_framework.generics import ListAPIView
from .models import Post
from .pagination import StandardResultsSetPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes

# # # ----------------- Post -----------------



@extend_schema(
    description="Create a new post with optional images/videos",
    request={
        "multipart/form-data": {  # لأننا نرسل ملفات
            "type": "object",
            "properties": {
                "content": {"type": "string"},
                "images": {
                    "type": "array",
                    "items": {"type": "string", "format": "binary"},
                    "description": "Optional images for the post"
                },
                "video": {"type": "string", "format": "binary", "description": "Optional single video"}
            }
        }
    },
    responses={
        201: {
            "type": "object",
            "properties": {
                "message": {"type": "string"},
                "post_id": {"type": "integer"}
            }
        }
    }
)
class PostView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        content = request.data.get("content")
        files = request.FILES.getlist("files")

        post = Post.objects.create(
            author=request.user,
            content=content
        )

        for file in files:
            PostMedia.objects.create(
                post=post,
                file=file
            )

        return Response({"message": "Post created"})






@extend_schema(
    description="Get paginated list of posts with media, likes, comments and follow info",
    responses={
        200: {
            "type": "object",
            "properties": {
                "count": {"type": "integer"},
                "next": {"type": "string", "nullable": True},
                "previous": {"type": "string", "nullable": True},
                "results": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "integer"},
                            "content": {"type": "string"},
                            "author": {"type": "string"},
                            "likes": {"type": "integer"},
                            "comments": {"type": "integer"},
                            "media": {"type": "array", "items": {"type": "string"}},
                            "is_liked": {"type": "boolean"},
                            "is_following": {"type": "boolean"},
                            "created_at": {"type": "string"}
                        }
                    }
                }
            }
        }
    }
)
class PostListView(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get(self, request):
        queryset = Post.objects.all().order_by('-created_at')
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request)
        data = []
        for post in page:
            data.append({
                "id": post.id,
                "content": post.content,
                "author": post.author.username,
                "likes": post.likes_count,
                "comments": post.comments_count,
                "media": [m.file.url for m in getattr(post, 'media', [])],  # كل الصور والفيديوهات
                "is_liked": post.likes.filter(user=request.user).exists(),
                "is_following": request.user.following.filter(id=post.author.id).exists(),
                "created_at": post.created_at
            })
        return paginator.get_paginated_response(data)
# ----------------- Comment -----------------



# تعديل بوست
@extend_schema(
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "content": {"type": "string"},
                "image": {"type": "string"},
                "video": {"type": "string"}
            }
        }
  },
    responses={200: {"type": "object", "properties": {"message": {"type": "string"}}}}
)
class UpdatePostView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request, post_id):
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return Response({"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND)

        if post.author != request.user:
            return Response({"error": "You can only edit your own posts"}, status=status.HTTP_403_FORBIDDEN)

        data = request.data
        if "content" in data:
            post.content = data["content"]
        if "image" in data:
            post.image = data["image"]
        if "video" in data:
            post.video = data["video"]

        post.save()
        return Response({"message": "Post updated successfully"}, status=status.HTTP_200_OK)


# حذف بوست
@extend_schema(
    responses={200: {"type": "object", "properties": {"message": {"type": "string"}}}}
)
class DeletePostView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, post_id):
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return Response({"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND)

        if post.author != request.user:
            return Response({"error": "You can only delete your own posts"}, status=status.HTTP_403_FORBIDDEN)

        post.delete()
        return Response({"message": "Post deleted successfully"}, status=status.HTTP_200_OK)


@extend_schema(
    description="Create, list, or delete comments",
    request={
        "application/json": {
            "type": "object",
            "properties": {"content": {"type": "string"}}
        }
    },
    responses={201: {"type": "object", "properties": {"message": {"type": "string"}, "comment_id": {"type": "integer"}}}}
)
class CommentView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, post_id):
        user = request.user
        content = request.data.get('content')
        post = get_object_or_404(Post, id=post_id)
        comment = Comment.objects.create(post=post, user=user, content=content)
        return Response({"message": "Comment added", "comment_id": comment.id}, status=201)

    def get(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        comments = post.comments.all().order_by('-created_at')
        data = []
        for c in comments:
            data.append({
                "id": c.id,
                "user": c.user.username,
                "content": c.content,
                "likes_count": c.likes_count,
                "created_at": c.created_at
            })
        return Response(data, status=200)


@extend_schema(
    description="Get paginated comments for a post",
    responses={
        200: {
            "type": "object",
            "properties": {
                "count": {"type": "integer"},
                "next": {"type": "string", "nullable": True},
                "previous": {"type": "string", "nullable": True},
                "results": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "integer"},
                            "content": {"type": "string"},
                            "user": {"type": "string"},
                            "likes": {"type": "integer"},
                            "created_at": {"type": "string"}
                        }
                    }
                }
            }
        }
    }
)
class CommentListView(ListAPIView):
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        post_id = self.kwargs['post_id']
        return Comment.objects.filter(post_id=post_id).order_by('-created_at')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)

        data = []
        for comment in page:
            data.append({
                "id": comment.id,
                "content": comment.content,
                "user": comment.user.username,
                "likes": comment.likes_count,
                "created_at": comment.created_at
            })

        return self.get_paginated_response(data)


from .models import Comment, CommentReaction

@extend_schema(
    description="Get paginated comments for a post with replies and reactions",
    responses={
        200: OpenApiResponse(
            response={
                "type": "object",
                "properties": {
                    "count": {"type": "integer"},
                    "next": {"type": "string", "nullable": True},
                    "previous": {"type": "string", "nullable": True},
                    "results": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "integer"},
                                "content": {"type": "string"},
                                "user": {"type": "string"},
                                "likes": {"type": "integer"},
                                "created_at": {"type": "string"},
                                "reactions": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "user": {"type": "string"},
                                            "emoji": {"type": "string"}
                                        }
                                    }
                                },
                                "replies": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "id": {"type": "integer"},
                                            "content": {"type": "string"},
                                            "user": {"type": "string"},
                                            "likes": {"type": "integer"},
                                            "created_at": {"type": "string"},
                                            "reactions": {
                                                "type": "array",
                                                "items": {
                                                    "type": "object",
                                                    "properties": {
                                                        "user": {"type": "string"},
                                                        "emoji": {"type": "string"}
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        )
    }
)
class CommentListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        post_id = self.kwargs['post_id']
        # التعليقات الأساسية فقط (parent=None)
        return Comment.objects.filter(post_id=post_id, parent=None).order_by('-created_at')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        data = []
        for comment in page:
            # التفاعلات على التعليق الأساسي
            reactions = [{"user": r.user.username, "emoji": r.emoji} for r in comment.reactions.all()]
            # الردود على التعليق
            replies = []
            for reply in comment.replies.all():
                reply_reactions = [{"user": rr.user.username, "emoji": rr.emoji} for rr in reply.reactions.all()]
                replies.append({
                    "id": reply.id,
                    "content": reply.content,
                    "user": reply.user.username,
                    "likes": reply.likes_count,
                    "created_at": reply.created_at,
                    "reactions": reply_reactions
                })

            data.append({
                "id": comment.id,
                "content": comment.content,
                "user": comment.user.username,
                "likes": comment.likes_count,
                "created_at": comment.created_at,
                "reactions": reactions,
                "replies": replies
            })

        return self.get_paginated_response(data)
@extend_schema(
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "content": {"type": "string"}
            }
        }
    },
    responses={200: {"type": "object", "properties": {"message": {"type": "string"}}}}
)
@extend_schema(
    description="Reply to a comment",
    request={
        "type": "object",
        "properties": {
            "content": {"type": "string", "description": "Reply text"}
        },
        "required": ["content"]
    },
    responses={
        201: {
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "content": {"type": "string"},
                "user": {"type": "string"},
                "likes": {"type": "integer"},
                "created_at": {"type": "string"},
                "reactions": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "user": {"type": "string"},
                            "emoji": {"type": "string"}
                        }
                    }
                }
            }
        }
    }
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reply_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    content = request.data.get("content")
    reply = Comment.objects.create(
        content=content,
        user=request.user,
        post=comment.post,
        parent=comment
    )
    return Response({
        "id": reply.id,
        "content": reply.content,
        "user": reply.user.username,
        "likes": 0,
        "created_at": reply.created_at,
        "reactions": []
    }, status=201)



@extend_schema(
    description="React to a comment (emoji)",
    request={
        "type": "object",
        "properties": {
            "emoji": {"type": "string", "description": "Emoji code or symbol"}
        },
        "required": ["emoji"]
    },
    responses={
        200: {
            "type": "object",
            "properties": {
                "comment_id": {"type": "integer"},
                "emoji": {"type": "string"},
                "user": {"type": "string"},
                "message": {"type": "string"}
            }
        }
    }
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def react_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    emoji = request.data.get("emoji")
    reaction, created = CommentReaction.objects.get_or_create(
        user=request.user,
        comment=comment,
        emoji=emoji
    )
    if not created:
        reaction.delete()
        return Response({
            "comment_id": comment.id,
            "emoji": emoji,
            "user": request.user.username,
            "message": "Reaction removed"
        })
    return Response({
        "comment_id": comment.id,
        "emoji": emoji,
        "user": request.user.username,
        "message": "Reaction added"
    }) 
class UpdateCommentView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request, comment_id):
        try:
            comment = Comment.objects.get(id=comment_id)
        except Comment.DoesNotExist:
            return Response({"error": "Comment not found"}, status=status.HTTP_404_NOT_FOUND)

        # تحقق: فقط صاحب التعليق
        if comment.user != request.user:
            return Response({"error": "You can only edit your own comments"}, status=status.HTTP_403_FORBIDDEN)

        comment.content = request.data.get("content", comment.content)
        comment.save()

        return Response({"message": "Comment updated successfully"}, status=status.HTTP_200_OK)



@extend_schema(
    responses={200: {"type": "object", "properties": {"message": {"type": "string"}}}}
)
class DeleteCommentView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, comment_id):
        try:
            comment = Comment.objects.get(id=comment_id)
        except Comment.DoesNotExist:
            return Response({"error": "Comment not found"}, status=status.HTTP_404_NOT_FOUND)

        # تحقق: فقط صاحب التعليق
        if comment.user != request.user:
            return Response({"error": "You can only delete your own comments"}, status=status.HTTP_403_FORBIDDEN)

        comment.delete()
        return Response({"message": "Comment deleted successfully"}, status=status.HTTP_200_OK)


# ----------------- Post Like -----------------




@extend_schema(
    responses={200: {"type": "object", "properties": {
        "message": {"type": "string"},
        "liked": {"type": "boolean"}
    }}}
)
class TogglePostLikeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, post_id):
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return Response({"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND)

        like, created = Like.objects.get_or_create(
            post=post,
            user=request.user
        )

        if not created:
            like.delete()
            return Response({
                "message": "Like removed",
                "liked": False
            }, status=status.HTTP_200_OK)

        return Response({
            "message": "Post liked",
            "liked": True
        }, status=status.HTTP_200_OK)





@extend_schema(
    responses={200: {"type": "object", "properties": {
        "message": {"type": "string"},
        "liked": {"type": "boolean"}
    }}}
)
class ToggleCommentLikeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, comment_id):
        try:
            comment = Comment.objects.get(id=comment_id)
        except Comment.DoesNotExist:
            return Response({"error": "Comment not found"}, status=status.HTTP_404_NOT_FOUND)

        like, created = CommentLike.objects.get_or_create(
            comment=comment,
            user=request.user
        )

        if not created:
            like.delete()
            return Response({
                "message": "Like removed",
                "liked": False
            }, status=status.HTTP_200_OK)

        return Response({
            "message": "Comment liked",
            "liked": True
        }, status=status.HTTP_200_OK)

# ----------------- Follow -----------------

@extend_schema(
    request=None,
    responses={
        200: OpenApiResponse(
            response={
                "type": "object",
                "properties": {
                    "message": {"type": "string"},
                    "following": {"type": "boolean"}
                }
            },
            description="Followed or Unfollowed successfully"
        ),
        400: OpenApiResponse(
            response={
                "type": "object",
                "properties": {
                    "error": {"type": "string"}
                }
            },
            description="Invalid action (e.g., follow yourself)"
        ),
        404: OpenApiResponse(
            response={
                "type": "object",
                "properties": {
                    "error": {"type": "string"}
                }
            },
            description="User not found"
        )
    },
    summary="Follow or unfollow a user",
    description="Authenticated user can follow or unfollow another user."
)
class ToggleFollowView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, user_id):
        try:
            target_user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        # ❌ منع متابعة النفس
        if request.user == target_user:
            return Response({"error": "You cannot follow yourself"}, status=status.HTTP_400_BAD_REQUEST)

        follow, created = Follow.objects.get_or_create(
            follower=request.user,
            following=target_user
        )

        # 🔁 Toggle
        if not created:
            follow.delete()
            return Response({
                "message": "Unfollowed",
                "following": False
            }, status=status.HTTP_200_OK)

        return Response({
            "message": "Followed",
            "following": True
        }, status=status.HTTP_200_OK)
@extend_schema(
    responses=OpenApiResponse(
        response=list,
        description="List of followers",
     
    ),
    summary="Get followers of a user",
)
class FollowersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        users = User.objects.filter(following__following_id=user_id)

        data = [{"id": u.id, "username": u.username} for u in users]
        return Response(data)
@extend_schema(
    responses=OpenApiResponse(
        response=list,
        description="List of users that this user is following",
     
    ),
    summary="Get users that a user is following",
)
class FollowingView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        users = User.objects.filter(followers__follower_id=user_id)

        data = [{"id": u.id, "username": u.username} for u in users]
        return Response(data)
@extend_schema(
    responses=OpenApiResponse(
        response=list,
        description="Suggested users to follow",
  
    ),
    summary="Get suggestions for users to follow",
)
class SuggestionsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        users = User.objects.exclude(id=request.user.id).order_by('?')[:5]

        data = [{"id": u.id, "username": u.username} for u in users]
        return Response(data)

@extend_schema(
    responses={
        200: {
            "type": "object",
            "properties": {
                "count": {"type": "integer"},
                "next": {"type": "string", "nullable": True},
                "previous": {"type": "string", "nullable": True},
                "results": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "integer"},
                            "content": {"type": "string", "nullable": True},
                            "author": {"type": "string"},
                            "likes": {"type": "integer"},
                            "comments": {"type": "integer"},
                            "is_liked": {"type": "boolean"},
                            "created_at": {"type": "string", "format": "date-time"}
                        }
                    }
                }
            }
        }
    }
)
class FeedView(ListAPIView):
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        following_users = self.request.user.following.all()
        return Post.objects.filter(author__in=following_users).order_by('-created_at')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)

        data = []
        for post in page:
            data.append({
                "id": post.id,
                "content": post.content,
                "author": post.author.username,
                "likes": post.likes_count,
                "comments": post.comments_count,
                "is_liked": post.likes.filter(user=request.user).exists(),
                "is_saved": post.saved_by.filter(user=request.user).exists(),
                "created_at": post.created_at
            })

        return self.get_paginated_response(data)


class SharePostView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, post_id):
        receiver_id = request.data.get("receiver_id")

        post = Post.objects.get(id=post_id)
        receiver = User.objects.get(id=receiver_id)

        Share.objects.create(
            post=post,
            sender=request.user,
            receiver=receiver
        )

        return Response({"message": "Post shared"})

@extend_schema(
    description="Toggle save/unsave post",
    responses={
        200: {
            "type": "object",
            "properties": {
                "message": {"type": "string"}
            }
        }
    }
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_save_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    saved, created = SavedPost.objects.get_or_create(
        user=request.user,
        post=post
    )

    if not created:
        saved.delete()
        return Response({"message": "Post unsaved"})

    return Response({"message": "Post saved"})

#   عرض البوستات المحفوظ______



@extend_schema(
    description="Get saved posts",
    responses={
        200: {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "content": {"type": "string"},
                    "author": {"type": "string"},
                    "media": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "likes": {"type": "integer"},
                    "comments": {"type": "integer"},
                    "is_saved": {"type": "boolean"},
                    "created_at": {"type": "string"}
                }
            }
        }
    }
)
class SavedPostsView(ListAPIView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Post.objects.filter(
            saved_by__user=self.request.user
        ).order_by('-created_at')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        data = []
        for post in queryset:
            data.append({
                "id": post.id,
                "content": post.content,
                "author": post.author.username,
                "media": [m.file.url for m in post.media.all()],
                "likes": post.likes_count,
                "comments": post.comments_count,
                "is_saved": True,
                "created_at": post.created_at
            })

        return Response(data)















