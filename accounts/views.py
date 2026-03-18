from django.shortcuts import render
from django.conf import settings
from drf_spectacular.utils import extend_schema
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import User
import random
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from rest_framework_simplejwt.tokens import RefreshToken

# --------------------------
# تسجيل حساب مع OTP
# --------------------------
@extend_schema(
    request={
        "application/json": {
            "type": "object",
            "properties": {"username": {"type": "string"}, "email": {"type": "string"}, "password": {"type": "string"}}
        }
    }
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
        user.save()

        send_otp_email(user, otp)

        return Response({"message": "User registered. Check email for OTP."}, status=201)

# --------------------------
# دالة إرسال OTP
# --------------------------
def send_otp_email(user, otp):
    subject = "Your CNTIC Verification Code"
    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = [user.email]
    html_content = render_to_string('email/otp_email.html', {'username': user.username, 'otp_code': otp})
    msg = EmailMultiAlternatives(subject, '', from_email, to_email)
    msg.attach_alternative(html_content, "text/html")
    msg.send(fail_silently=False)

# --------------------------
# التحقق من OTP
# --------------------------
@extend_schema(
    request={
        "application/json": {
            "type": "object",
            "properties": {"email": {"type": "string"}, "otp": {"type": "integer"}}
        }
    }
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

# --------------------------
# إعادة إرسال OTP
# --------------------------
@extend_schema(
    request={"application/json": {"type": "object", "properties": {"email": {"type": "string"}}}}
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

        otp = random.randint(100000, 999999)
        user.otp_code = otp
        user.save()
        send_otp_email(user, otp)

        return Response({"message": "OTP resent successfully"}, status=200)
        # --------------------------
# تسجيل الدخول JWT
# --------------------------
@extend_schema(
    request={
        "application/json": {
            "type": "object",
            "properties": {"email": {"type": "string"}, "password": {"type": "string"}}
        }
    }
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

        refresh = RefreshToken.for_user(user)
        return Response({"refresh": str(refresh), "access": str(refresh.access_token)})

# --------------------------
# صفحة البروفايل
# --------------------------




@extend_schema(
    responses={
        200: {
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "username": {"type": "string"},
                "email": {"type": "string"},
                "profile_picture": {"type": "string", "nullable": True},
                "bio": {"type": "string", "nullable": True},
            }
        }
    }
)

class ProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "profile_picture": user.profile_picture.url if user.profile_picture else None,
            "bio": user.bio if hasattr(user, 'bio') else None,
        })