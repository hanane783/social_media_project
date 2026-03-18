from django.shortcuts import render

# Create your views here.

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from drf_spectacular.utils import extend_schema
from django.shortcuts import get_object_or_404
from .models import Post, Comment, Like, CommentLike, Follow
from accounts.models import User
from rest_framework.generics import ListAPIView
from .models import Post
from .pagination import StandardResultsSetPagination
from rest_framework.permissions import IsAuthenticated

# ----------------- Post -----------------
@extend_schema(
    description="Create or list posts",
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "content": {"type": "string"},
                "image": {"type": "string", "format": "binary"},
                "video": {"type": "string", "format": "binary"}
            }
        }
    },
    responses={201: {"type": "object", "properties": {"message": {"type": "string"}, "post_id": {"type": "integer"}}}}
)
class PostView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        content = request.data.get('content')
        image = request.data.get('image')
        video = request.data.get('video')

        post = Post.objects.create(author=user, content=content, image=image, video=video)
        return Response({"message": "Post created", "post_id": post.id}, status=201)

    def get(self, request):
        posts = Post.objects.all().order_by('-created_at')
        data = []
        for p in posts:
            data.append({
                "id": p.id,
                "author": p.author.username,
                "content": p.content,
                "image": p.image.url if p.image else None,
                "video": p.video.url if p.video else None,
                "likes_count": p.likes_count,
                "comments_count": p.comments_count,
                "created_at": p.created_at
            })
        return Response(data, status=200)

@extend_schema(
    description="Get paginated list of posts",
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
                            "image": {"type": "string", "nullable": True},
                            "video": {"type": "string", "nullable": True},
                            "created_at": {"type": "string"}
                        }
                    }
                }
            }
        }
    }
)


class PostListView(ListAPIView):
    queryset = Post.objects.all().order_by('-created_at')
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)

        data = []
        for post in page:
            data.append({
                "id": post.id,
                "content": post.content,
                "author": post.author.username,

                # 🔥 Counts
                "likes": post.likes_count,
                "comments": post.comments_count,

                # 🎥 Media
                "image": post.image.url if post.image else None,
                "video": post.video.url if post.video else None,

                # 🧠 Smart fields
                "is_liked": post.likes.filter(user=request.user).exists(),
                "is_following": request.user.following.filter(id=post.author.id).exists(),

                "created_at": post.created_at
            })

        return self.get_paginated_response(data)
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
    responses={200: {"type": "object", "properties": {
        "message": {"type": "string"},
        "following": {"type": "boolean"}
    }}}
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
                "created_at": post.created_at
            })

        return self.get_paginated_response(data)