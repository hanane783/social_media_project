

from django.db import models
from accounts.models import User  # الموديل الأساسي للمستخدم

# ----------------- Post -----------------
class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    content = models.TextField(blank=True, default="")  # قيمة افتراضية لتجنب مشاكل الميجريشن
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def likes_count(self):
        return self.likes.count()

    @property
    def comments_count(self):
        return self.comments.count()

    def str(self):
        return f"Post by {self.author.username} ({self.created_at})"

        # ___________postmedia_________________
class PostMedia(models.Model):
    post = models.ForeignKey(Post, related_name='media', on_delete=models.CASCADE)
    file = models.FileField(upload_to='post_media/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
# save post---------------------------
class SavedPost(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_posts')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='saved_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')  # يمنع حفظ نفس البوست مرتين


# ----------------- Comment -----------------
class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField(blank=True, default="")  # إضافة default
    created_at = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')

    @property
    def likes_count(self):
        return self.likes.count()

    def str(self):
        return f"Comment by {self.user.username} on Post {self.post.id}"


# ----------------- Like للبوسات -----------------
class Like(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('post', 'user')

    def str(self):
        return f"{self.user.username} likes Post {self.post.id}"


# ----------------- Like للتعليقات -----------------
class CommentLike(models.Model):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('comment', 'user')

    def str(self):
        return f"{self.user.username} likes Comment {self.comment.id}"
# comment reaction______________
class CommentReaction(models.Model):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='reactions')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    emoji = models.CharField(max_length=10)  # مثال: "❤️", "😂", "👍"
    
    class Meta:
        unique_together = ('comment', 'user', 'emoji')  # يمنع نفس 

# ----------------- Follow -----------------
class Follow(models.Model):
    follower = models.ForeignKey(User, related_name='following', on_delete=models.CASCADE)
    following = models.ForeignKey(User, related_name='followers', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('follower', 'following')

    def str(self):
        return f"{self.follower.username} follows {self.following.username}"



        # ___________________________
class Share(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='received_shares', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)