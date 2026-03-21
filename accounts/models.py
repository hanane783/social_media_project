

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

class User(AbstractUser):
    is_verified = models.BooleanField(default=False)  # للتحقق من البريد
    otp_code = models.IntegerField(null=True, blank=True)  # لتخزين OTP
    last_otp_sent = models.DateTimeField(null=True, blank=True)  # وقت آخر إرسال OTP
    profile_picture = models.ImageField(upload_to='profiles/', null=True, blank=True)  # صورة المستخدم
    bio = models.TextField(blank=True, null=True)  # نبذة عن المستخدم
    last_seen = models.DateTimeField(null=True, blank=True)  # آخر ظهور
    is_online = models.BooleanField(default=False)  # حالة الاتصال
    following = models.ManyToManyField('self', symmetrical=False, related_name='followers', blank=True)  # المتابعين

    def __str__(self):
        return self.username  
