

from django.urls import path
from .views import (
    RegisterView, VerifyOTPView, ResendOTPView, LoginView,
    ProfileView, SearchUserView, update_profile, change_password
)

app_name = 'accounts'

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify_otp'),
    path('resend-otp/', ResendOTPView.as_view(), name='resend_otp'),
    path('login/', LoginView.as_view(), name='login'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('search/', SearchUserView.as_view(), name='search-users'),
    path('update-profile/', update_profile, name='update-profile'),
    path('change-password/', change_password, name='change-password'),
]