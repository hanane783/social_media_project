# from django.shortcuts import render
# from django.conf import settings
# from drf_spectacular.utils import extend_schema
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status, permissions
# from rest_framework.permissions import IsAuthenticated
# from .models import User
# import random
# from django.core.mail import EmailMultiAlternatives
# from django.template.loader import render_to_string
# from rest_framework_simplejwt.tokens import RefreshToken
# from rest_framework.decorators import permission_classes
# from rest_framework.decorators import api_view

# # --------------------------
# # تسجيل حساب مع OTP
# # --------------------------
# @extend_schema(
#     request={
#         "application/json": {
#             "type": "object",
#             "properties": {"username": {"type": "string"}, "email": {"type": "string"}, "password": {"type": "string"}}
#         }
#     }
# )
# class RegisterView(APIView):
#     def post(self, request):
#         username = request.data.get('username')
#         email = request.data.get('email')
#         password = request.data.get('password')

#         if not username or not email or not password:
#             return Response({"error": "All fields required"}, status=400)

#         if User.objects.filter(username=username).exists():
#             return Response({"error": "Username exists"}, status=400)

#         if User.objects.filter(email=email).exists():
#             return Response({"error": "Email exists"}, status=400)

#         otp = random.randint(100000, 999999)
#         user = User(username=username, email=email, is_verified=False, otp_code=otp)
#         user.set_password(password)
#         user.save()

#         send_otp_email(user, otp)

#         return Response({"message": "User registered. Check email for OTP."}, status=201)

# # --------------------------
# # دالة إرسال OTP
# # --------------------------
# def send_otp_email(user, otp):
#     subject = "Your CNTIC Verification Code"
#     from_email = settings.DEFAULT_FROM_EMAIL
#     to_email = [user.email]
#     html_content = render_to_string('email/otp_email.html', {'username': user.username, 'otp_code': otp})
#     msg = EmailMultiAlternatives(subject, '', from_email, to_email)
#     msg.attach_alternative(html_content, "text/html")
#     msg.send(fail_silently=False)

# # --------------------------
# # التحقق من OTP
# # --------------------------
# @extend_schema(
#     request={
#         "application/json": {
#             "type": "object",
#             "properties": {"email": {"type": "string"}, "otp": {"type": "integer"}}
#         }
#     }
# )
# class VerifyOTPView(APIView):
#     def post(self, request):
#         email = request.data.get('email')
#         otp = request.data.get('otp')

#         if not email or not otp:
#             return Response({"error": "Email and OTP required"}, status=400)

#         try:
#             user = User.objects.get(email=email)
#         except User.DoesNotExist:
#             return Response({"error": "User not found"}, status=404)

#         if user.is_verified:
#             return Response({"message": "Account already verified"}, status=200)

#         if user.otp_code != int(otp):
#             return Response({"error": "Invalid OTP"}, status=400)

#         user.is_verified = True
#         user.otp_code = None
#         user.save()

#         return Response({"message": "Account verified successfully"}, status=200)

# # --------------------------
# # إعادة إرسال OTP
# # --------------------------
# @extend_schema(
#     request={"application/json": {"type": "object", "properties": {"email": {"type": "string"}}}}
# )
# class ResendOTPView(APIView):
#     def post(self, request):
#         email = request.data.get('email')

#         if not email:
#             return Response({"error": "Email is required"}, status=400)

#         try:
#             user = User.objects.get(email=email)
#         except User.DoesNotExist:
#             return Response({"error": "User not found"}, status=404)

#         if user.is_verified:
#             return Response({"error": "Account already verified"}, status=400)


            
#         # 🚨 تحقق من الوقت
#         if user.last_otp_sent:
#             diff = timezone.now() - user.last_otp_sent
#             if diff < timedelta(seconds=30):
#                 return Response({
#                     "error": "Wait 30 seconds before requesting new OTP"
#                 }, status=429)

#         otp = random.randint(100000, 999999)
#         user.otp_code = otp
#         user.save()
#         send_otp_email(user, otp)

#         return Response({"message": "OTP resent successfully"}, status=200)
#         # --------------------------
# # تسجيل الدخول JWT
# # --------------------------
# @extend_schema(
#     request={
#         "application/json": {
#             "type": "object",
#             "properties": {"email": {"type": "string"}, "password": {"type": "string"}}
#         }
#     }
# )
# class LoginView(APIView):
#     def post(self, request):
#         email = request.data.get('email')
#         password = request.data.get('password')

#         if not email or not password:
#             return Response({"error": "Email and password required"}, status=400)

#         try:
#             user = User.objects.get(email=email)
#         except User.DoesNotExist:
#             return Response({"error": "Invalid credentials"}, status=401)

#         if not user.check_password(password):
#             return Response({"error": "Invalid credentials"}, status=401)

#         if not user.is_verified:
#             return Response({"error": "Account not verified"}, status=403)

#         refresh = RefreshToken.for_user(user)
#         return Response({"refresh": str(refresh), "access": str(refresh.access_token)})

# # --------------------------
# # صفحة البروفايل
# # --------------------------




# @extend_schema(
#     responses={
#         200: {
#             "type": "object",
#             "properties": {
#                 "id": {"type": "integer"},
#                 "username": {"type": "string"},
#                 "email": {"type": "string"},
#                 "profile_picture": {"type": "string", "nullable": True},
#                 "bio": {"type": "string", "nullable": True},
#             }
#         }
#     }
# )

# class ProfileView(APIView):
#     permission_classes = [permissions.IsAuthenticated]

#     def get(self, request):
#         user = request.user
#         return Response({
#             "id": user.id,
#             "username": user.username,
#             "email": user.email,
#             "profile_picture": user.profile_picture.url if user.profile_picture else None,
#             "bio": user.bio if hasattr(user, 'bio') else None,
#         })



# @extend_schema(
#     parameters=[{"name": "username", "required": True, "type": "string"}],
#     responses={200: {"type": "array"}}
# )
# class SearchUserView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         username = request.GET.get('username', '')
#         users = User.objects.filter(username__icontains=username)

#         data = []
#         for u in users:
#             data.append({
#                 "id": u.id,
#                 "username": u.username,
#                 "is_following": request.user.following.filter(id=u.id).exists()
#             })

#         return Response(data)

# @api_view(['PUT'])
# @permission_classes([IsAuthenticated])
# def update_profile(request):
#     user = request.user

#     user.username = request.data.get('username', user.username)
#     user.bio = request.data.get('bio', user.bio)
#     user. profile_picture = request.data.get(' profile_picture ',user. profile_picture )

#     user.save()

#     return Response({"message": "Profile updated"})

    
# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def change_password(request):
#     user = request.user

#     if not user.check_password(request.data['old_password']):
#         return Response({"error": "Wrong password"}, status=400)

#     user.set_password(request.data['new_password'])
#     user.save()

#     return Response({"message": "Password updated"})
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema
from .models import User
import random

# -------------------------- Helper: send OTP --------------------------
def send_otp_email(user, otp):
    """
    دالة لإرسال OTP للمستخدم بالبريد الإلكتروني
    """
    subject = "Your CNTIC Verification Code"
    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = [user.email]
    html_content = render_to_string('email/otp_email.html', {'username': user.username, 'otp_code': otp})
    msg = EmailMultiAlternatives(subject, '', from_email, to_email)
    msg.attach_alternative(html_content, "text/html")
    msg.send(fail_silently=False)

# -------------------------- Register --------------------------
@extend_schema(
    request={
        "application/json": {
            "type": "object",
            "properties": {"username": {"type": "string"}, "email": {"type": "string"}, "password": {"type": "string"}}
        }
    },
    responses={201: {"type": "object", "properties": {"message": {"type": "string"}}}}
)
class RegisterView(APIView):
    def post(self, request):
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')

        if not username or not email or not password:
            return Response({"error": "All fields required"}, status=400)

        if User.objects.filter(username=username).exists():
            return Response({"error": "Username exists"}, status=400)
        if User.objects.filter(email=email).exists():
            return Response({"error": "Email exists"}, status=400)

        otp = random.randint(100000, 999999)
        user = User(username=username, email=email, is_verified=False, otp_code=otp)
        user.set_password(password)
        user.last_otp_sent = timezone.now()
        user.save()

        send_otp_email(user, otp)

        return Response({"message": "User registered. Check email for OTP."}, status=201)

# -------------------------- Verify OTP --------------------------
@extend_schema(
    request={
        "application/json": {
            "type": "object",
            "properties": {"email": {"type": "string"}, "otp": {"type": "integer"}}
        }
    },
    responses={200: {"type": "object", "properties": {"message": {"type": "string"}}}}
)
class VerifyOTPView(APIView):
    def post(self, request):
        email = request.data.get('email')
        otp = request.data.get('otp')

        if not email or not otp:
            return Response({"error": "Email and OTP required"}, status=400)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)

        if user.is_verified:
            return Response({"message": "Account already verified"}, status=200)
        if user.otp_code != int(otp):
            return Response({"error": "Invalid OTP"}, status=400)

        user.is_verified = True
        user.otp_code = None
        user.save()

        return Response({"message": "Account verified successfully"}, status=200)

# -------------------------- Resend OTP --------------------------
@extend_schema(
    request={"application/json": {"type": "object", "properties": {"email": {"type": "string"}}}},
    responses={200: {"type": "object", "properties": {"message": {"type": "string"}}}}
)
class ResendOTPView(APIView):
    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({"error": "Email is required"}, status=400)
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)

        if user.is_verified:
            return Response({"error": "Account already verified"}, status=400)

        if user.last_otp_sent and (timezone.now() - user.last_otp_sent) < timedelta(seconds=30):
            return Response({"error": "Wait 30 seconds before requesting new OTP"}, status=429)

        otp = random.randint(100000, 999999)
        user.otp_code = otp
        user.last_otp_sent = timezone.now()
        user.save()
        send_otp_email(user, otp)

        return Response({"message": "OTP resent successfully"}, status=200)

# -------------------------- Login --------------------------
@extend_schema(
    request={
        "application/json": {
            "type": "object",
            "properties": {"email": {"type": "string"}, "password": {"type": "string"}}
        }
    },
    responses={200: {"type": "object", "properties": {"refresh": {"type": "string"}, "access": {"type": "string"}}}}
)
class LoginView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response({"error": "Email and password required"}, status=400)
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "Invalid credentials"}, status=401)

        if not user.check_password(password):
            return Response({"error": "Invalid credentials"}, status=401)
        if not user.is_verified:
            return Response({"error": "Account not verified"}, status=403)
        if not user.is_active:
            return Response({"error": "Account disabled"}, status=403)

        refresh = RefreshToken.for_user(user)
        return Response({"refresh": str(refresh), "access": str(refresh.access_token)})

# -------------------------- Profile --------------------------
@extend_schema(
    responses={200: {"type": "object", "properties": {
        "id": {"type": "integer"},
        "username": {"type": "string"},
        "email": {"type": "string"},
        "profile_picture": {"type": "string", "nullable": True},
        "bio": {"type": "string", "nullable": True},
    }}}
)
class ProfileView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user = request.user
        data = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "profile_picture": user.profile_picture.url if user.profile_picture else None,
            "bio": user.bio if user.bio else "",
        }
        return Response(data)

# -------------------------- Search Users --------------------------
@extend_schema(
    parameters=[{"name": "username", "required": True, "type": "string"}],
    responses={200: {"type": "array"}}
)
class SearchUserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        username = request.GET.get('username', '')
        users = User.objects.filter(username__icontains=username)
        data = []
        for u in users:
            data.append({
                "id": u.id,
                "username": u.username,
                "is_following": request.user.following.filter(id=u.id).exists()
            })
        return Response(data)

# -------------------------- Update Profile --------------------------
@extend_schema(
    request={"application/json": {"type": "object", "properties": {"username": {"type": "string"}, "bio": {"type": "string"}, "profile_picture": {"type": "string"}}}},
    responses={200: {"type": "object", "properties": {"message": {"type": "string"}}}}
)
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_profile(request):
    user = request.user
    user.username = request.data.get('username', user.username)
    user.bio = request.data.get('bio', user.bio)
    user.profile_picture = request.data.get('profile_picture', user.profile_picture)
    user.save()
    return Response({"message": "Profile updated"})

# -------------------------- Change Password --------------------------
@extend_schema(
    request={"application/json": {"type": "object", "properties": {"old_password": {"type": "string"}, "new_password": {"type": "string"}}}},
    responses={200: {"type": "object", "properties": {"message": {"type": "string"}}}}
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    user = request.user
    old_password = request.data.get('old_password')
    new_password = request.data.get('new_password')

    if not user.check_password(old_password):
        return Response({"error": "Wrong password"}, status=400)

    user.set_password(new_password)
    user.save()
    return Response({"message": "Password updated"})


