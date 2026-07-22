from django.urls import path

from .views import (
    AdminView,
    ForgotPasswordView,
    LoginView,
    LogoutView,
    ProfileView,
    RefreshTokenView,
    RegisterView,
    RequestEmailVerificationView,
    ResetPasswordView,
    SendOTPView,
    StaffView,
    VerifyEmailView,
    VerifyOTPView,
)

app_name = "accounts"

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("token/refresh/", RefreshTokenView.as_view(), name="token_refresh"),
    path("password/forgot/", ForgotPasswordView.as_view(), name="forgot_password"),
    path("password/reset/", ResetPasswordView.as_view(), name="reset_password"),
    path("email/verify/request/", RequestEmailVerificationView.as_view(), name="verify_email_request"),
    path("email/verify/", VerifyEmailView.as_view(), name="verify_email"),
    path("otp/send/", SendOTPView.as_view(), name="send_otp"),
    path("otp/verify/", VerifyOTPView.as_view(), name="verify_otp"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("admin-check/", AdminView.as_view(), name="admin_check"),
    path("staff-check/", StaffView.as_view(), name="staff_check"),
]
