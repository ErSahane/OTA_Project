from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase


class IAMAPITests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="tester",
            email="tester@example.com",
            password="StrongPass123!",
            role="customer",
        )
        self.user.is_verified = True
        self.user.save(update_fields=["is_verified"])

    def test_register_creates_user(self):
        response = self.client.post(
            reverse("accounts:register"),
            {
                "username": "newuser",
                "email": "new@example.com",
                "password": "StrongPass123!",
                "password_confirm": "StrongPass123!",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertTrue(get_user_model().objects.filter(email="new@example.com").exists())

    def test_login_returns_tokens(self):
        response = self.client.post(
            reverse("accounts:login"),
            {"email": "tester@example.com", "password": "StrongPass123!"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_refresh_token_returns_new_access_token(self):
        login_response = self.client.post(
            reverse("accounts:login"),
            {"email": "tester@example.com", "password": "StrongPass123!"},
            format="json",
        )
        refresh_response = self.client.post(
            reverse("accounts:token_refresh"),
            {"refresh": login_response.data["refresh"]},
            format="json",
        )
        self.assertEqual(refresh_response.status_code, 200)
        self.assertIn("access", refresh_response.data)

    def test_forgot_password_and_reset_flow(self):
        forgot_response = self.client.post(
            reverse("accounts:forgot_password"),
            {"email": "tester@example.com"},
            format="json",
        )
        self.assertEqual(forgot_response.status_code, 200)
        self.assertTrue(self.user.password_resets.exists())

        reset_token = self.user.password_resets.first().token
        reset_response = self.client.post(
            reverse("accounts:reset_password"),
            {"token": reset_token, "password": "NewPass123!", "password_confirm": "NewPass123!"},
            format="json",
        )
        self.assertEqual(reset_response.status_code, 200)

    def test_email_verification_flow(self):
        request_response = self.client.post(
            reverse("accounts:verify_email_request"),
            {"email": "tester@example.com"},
            format="json",
        )
        self.assertEqual(request_response.status_code, 200)
        self.assertTrue(self.user.email_verifications.exists())

        verification_token = self.user.email_verifications.first().token
        verify_response = self.client.post(
            reverse("accounts:verify_email"),
            {"token": verification_token},
            format="json",
        )
        self.assertEqual(verify_response.status_code, 200)
