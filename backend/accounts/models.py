from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True)
    role = models.CharField(max_length=30, default="customer")
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    class Meta:
        db_table = "auth_user"

    def __str__(self):
        return self.email


class UserProfile(models.Model):
    user = models.OneToOneField("accounts.User", related_name="profile", on_delete=models.CASCADE)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    phone = models.CharField(max_length=30, blank=True)
    avatar = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "user_profile"

    def __str__(self):
        return f"{self.user.email} profile"


class PasswordResetToken(models.Model):
    user = models.ForeignKey("accounts.User", related_name="password_resets", on_delete=models.CASCADE)
    token = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    used = models.BooleanField(default=False)

    class Meta:
        db_table = "password_reset_token"

    def is_expired(self):
        return timezone.now() >= self.expires_at


class EmailVerificationToken(models.Model):
    user = models.ForeignKey("accounts.User", related_name="email_verifications", on_delete=models.CASCADE)
    token = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    used = models.BooleanField(default=False)

    class Meta:
        db_table = "email_verification_token"

    def is_expired(self):
        return timezone.now() >= self.expires_at


class OTPCode(models.Model):
    user = models.ForeignKey("accounts.User", related_name="otps", on_delete=models.CASCADE)
    code = models.CharField(max_length=8)
    purpose = models.CharField(max_length=50, default="verification")
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    used = models.BooleanField(default=False)

    class Meta:
        db_table = "otp_code"

    def is_expired(self):
        return timezone.now() >= self.expires_at


class AuditLog(models.Model):
    user = models.ForeignKey("accounts.User", null=True, blank=True, on_delete=models.SET_NULL)
    action = models.CharField(max_length=100)
    details = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "audit_log"
