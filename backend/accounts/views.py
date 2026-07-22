import secrets
from datetime import timedelta
from random import randint

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.utils import timezone
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .models import AuditLog, EmailVerificationToken, OTPCode, PasswordResetToken, UserProfile
from .permissions import IsAdmin, IsStaffOrAdmin
from .serializers import (
    EmailVerificationSerializer,
    ForgotPasswordSerializer,
    LoginSerializer,
    RegisterSerializer,
    ResetPasswordSerializer,
    SendOTPSerializer,
    VerifyEmailSerializer,
    VerifyOTPSerializer,
)

User = get_user_model()


class RegisterView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        AuditLog.objects.create(user=user, action="register", details="User registered")
        return Response({"message": "User created successfully."}, status=status.HTTP_201_CREATED)


class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        if self._is_rate_limited(request):
            return Response({"detail": "Too many login attempts."}, status=status.HTTP_429_TOO_MANY_REQUESTS)
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = serializer.validated_data["user"] if isinstance(serializer.validated_data.get("user"), dict) else None
            if user is not None:
                user_obj = User.objects.get(id=user["id"])
                AuditLog.objects.create(user=user_obj, action="login", details="User logged in")
        return response

    def _is_rate_limited(self, request):
        identifier = request.data.get("email") or request.data.get("username") or request.META.get("REMOTE_ADDR")
        cache_key = f"login_attempts:{identifier}"
        attempts = cache.get(cache_key, 0)
        if attempts >= 5:
            return True
        cache.set(cache_key, attempts + 1, 60)
        return False


class LogoutView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        AuditLog.objects.create(user=request.user, action="logout", details="User logged out")
        return Response({"message": "Logged out successfully."}, status=status.HTTP_200_OK)


class RequestEmailVerificationView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = EmailVerificationSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"message": "If the email exists, a verification link has been sent."}, status=status.HTTP_200_OK)

        token = secrets.token_urlsafe(32)
        EmailVerificationToken.objects.create(
            user=user,
            token=token,
            expires_at=timezone.now() + timedelta(days=1),
        )
        AuditLog.objects.create(user=user, action="email_verification_requested", details="Email verification requested")
        return Response({"message": "If the email exists, a verification link has been sent."}, status=status.HTTP_200_OK)


class VerifyEmailView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = VerifyEmailSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.validated_data["token"]
        try:
            verification_token = EmailVerificationToken.objects.get(token=token, used=False)
        except EmailVerificationToken.DoesNotExist:
            return Response({"detail": "Invalid or expired token."}, status=status.HTTP_400_BAD_REQUEST)

        if verification_token.is_expired():
            return Response({"detail": "Invalid or expired token."}, status=status.HTTP_400_BAD_REQUEST)

        user = verification_token.user
        user.is_verified = True
        user.save(update_fields=["is_verified"])
        verification_token.used = True
        verification_token.save(update_fields=["used"])
        AuditLog.objects.create(user=user, action="email_verified", details="Email verified")
        return Response({"message": "Email verified successfully."}, status=status.HTTP_200_OK)


class SendOTPView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = SendOTPSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        purpose = serializer.validated_data.get("purpose", "verification")
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"message": "If the email exists, an OTP has been sent."}, status=status.HTTP_200_OK)

        code = f"{randint(100000, 999999):06d}"
        OTPCode.objects.create(user=user, code=code, purpose=purpose, expires_at=timezone.now() + timedelta(minutes=10))
        AuditLog.objects.create(user=user, action="otp_sent", details=f"OTP sent for {purpose}")
        return Response({"message": "OTP created successfully.", "code": code}, status=status.HTTP_200_OK)


class VerifyOTPView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = VerifyOTPSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        code = serializer.validated_data["code"]
        purpose = serializer.validated_data.get("purpose", "verification")
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"detail": "Invalid OTP."}, status=status.HTTP_400_BAD_REQUEST)

        otp = OTPCode.objects.filter(user=user, purpose=purpose, used=False).order_by("-created_at").first()
        if not otp or otp.is_expired() or otp.code != code:
            return Response({"detail": "Invalid OTP."}, status=status.HTTP_400_BAD_REQUEST)

        otp.used = True
        otp.save(update_fields=["used"])
        return Response({"message": "OTP verified successfully."}, status=status.HTTP_200_OK)


class RefreshTokenView(TokenRefreshView):
    permission_classes = [AllowAny]


class ForgotPasswordView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = ForgotPasswordSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"message": "If the email exists, a reset link has been sent."}, status=status.HTTP_200_OK)

        token = secrets.token_urlsafe(32)
        PasswordResetToken.objects.create(
            user=user,
            token=token,
            expires_at=timezone.now() + timedelta(minutes=15),
        )
        AuditLog.objects.create(user=user, action="forgot_password", details="Password reset requested")
        return Response({"message": "If the email exists, a reset link has been sent."}, status=status.HTTP_200_OK)


class ResetPasswordView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = ResetPasswordSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.validated_data["token"]
        password = serializer.validated_data["password"]
        try:
            reset_token = PasswordResetToken.objects.get(token=token, used=False)
        except PasswordResetToken.DoesNotExist:
            return Response({"detail": "Invalid or expired token."}, status=status.HTTP_400_BAD_REQUEST)

        if reset_token.is_expired():
            return Response({"detail": "Invalid or expired token."}, status=status.HTTP_400_BAD_REQUEST)

        user = reset_token.user
        user.set_password(password)
        user.save(update_fields=["password"])
        reset_token.used = True
        reset_token.save(update_fields=["used"])
        AuditLog.objects.create(user=user, action="reset_password", details="Password reset completed")
        return Response({"message": "Password reset successfully."}, status=status.HTTP_200_OK)


class ProfileView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        return Response({"email": request.user.email, "role": request.user.role})


class AdminView(GenericAPIView):
    permission_classes = [IsAdmin]

    def get(self, request, *args, **kwargs):
        return Response({"message": "Admin access granted."})


class StaffView(GenericAPIView):
    permission_classes = [IsStaffOrAdmin]

    def get(self, request, *args, **kwargs):
        return Response({"message": "Staff access granted."})
