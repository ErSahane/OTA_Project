from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import AuditLog, User
from .models import City, Country, Currency, StateRegion
from .import_export import ImportExportService


class MasterDataModelTests(TestCase):
    def test_soft_delete_marks_record_as_deleted(self):
        country = Country.objects.create(code="USA", name="United States")
        country.soft_delete()
        self.assertTrue(Country.objects.get(pk=country.pk).is_deleted)
        self.assertIsNotNone(Country.objects.get(pk=country.pk).deleted_at)


class MasterDataAPITests(APITestCase):
    def setUp(self):
        self.country = Country.objects.create(code="CAN", name="Canada")
        self.state = StateRegion.objects.create(country=self.country, code="ON", name="Ontario")
        self.city = City.objects.create(state=self.state, code="TOR", name="Toronto")
        self.currency = Currency.objects.create(code="CAD", name="Canadian Dollar", symbol="$")

        # Create user accounts for testing permissions
        self.admin_user = User.objects.create_user(
            username="admin",
            email="admin@astrovoyage.local",
            password="adminpassword",
            role="admin"
        )
        self.customer_user = User.objects.create_user(
            username="customer",
            email="customer@astrovoyage.local",
            password="customerpassword",
            role="customer"
        )

    def test_list_countries_anonymous(self):
        response = self.client.get(reverse("country-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should contain Canada
        self.assertTrue(any(item["code"] == "CAN" for item in response.data["results"]))

    def test_create_currency_anonymous_fails(self):
        response = self.client.post(
            reverse("currency-list"),
            {"code": "USD", "name": "US Dollar", "symbol": "$"},
            format="json",
        )
        # Writes are restricted to Staff/Admin
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_currency_customer_fails(self):
        self.client.force_authenticate(user=self.customer_user)
        response = self.client.post(
            reverse("currency-list"),
            {"code": "USD", "name": "US Dollar", "symbol": "$"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_currency_admin_succeeds_and_logs(self):
        self.client.force_authenticate(user=self.admin_user)
        initial_logs_count = AuditLog.objects.filter(action="currency_create").count()

        response = self.client.post(
            reverse("currency-list"),
            {"code": "USD", "name": "US Dollar", "symbol": "$"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Currency.objects.filter(code="USD").count(), 1)

        # Verify audit log entry
        new_logs_count = AuditLog.objects.filter(action="currency_create").count()
        self.assertEqual(new_logs_count, initial_logs_count + 1)
        latest_log = AuditLog.objects.filter(action="currency_create").latest("created_at")
        self.assertEqual(latest_log.user, self.admin_user)
        self.assertIn("Created Currency", latest_log.details)

    def test_update_currency_admin_succeeds_and_logs(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.put(
            reverse("currency-detail", kwargs={"pk": self.currency.pk}),
            {"code": "CAD", "name": "Canadian Dollar Updated", "symbol": "C$"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.currency.refresh_from_db()
        self.assertEqual(self.currency.name, "Canadian Dollar Updated")

        # Verify update audit log
        latest_log = AuditLog.objects.filter(action="currency_update").latest("created_at")
        self.assertEqual(latest_log.user, self.admin_user)

    def test_delete_currency_admin_succeeds_and_logs(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete(
            reverse("currency-detail", kwargs={"pk": self.currency.pk})
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verify soft delete
        self.currency.refresh_from_db()
        self.assertTrue(self.currency.is_deleted)

        # Verify delete audit log
        latest_log = AuditLog.objects.filter(action="currency_delete").latest("created_at")
        self.assertEqual(latest_log.user, self.admin_user)

    def test_dynamic_filtering(self):
        # Create another country and state
        usa = Country.objects.create(code="USA", name="United States")
        StateRegion.objects.create(country=usa, code="NY", name="New York")

        # Filter state regions by country_id
        response = self.client.get(reverse("state-region-list"), {"country_id": self.country.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data["results"]
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["code"], "ON")

        # Filter state regions by country code
        response = self.client.get(reverse("state-region-list"), {"country": usa.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data["results"]
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["code"], "NY")

    def test_import_export_api_permissions(self):
        # Anonymous should fail
        response = self.client.get(reverse("import-export-export"), {"model": "countries"})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Customer should fail
        self.client.force_authenticate(user=self.customer_user)
        response = self.client.get(reverse("import-export-export"), {"model": "countries"})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_import_export_api_succeeds_for_admin(self):
        self.client.force_authenticate(user=self.admin_user)
        
        # Test Export
        response = self.client.get(reverse("import-export-export"), {"model": "countries"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("csv", response.data)
        csv_content = response.data["csv"]
        self.assertIn("CAN,Canada", csv_content)

        # Test Import
        csv_import_data = f"id,country_id,code,name\n, {self.country.id},BC,British Columbia\n"
        response = self.client.post(
            reverse("import-export-import-data"),
            {"model": "states", "csv": csv_import_data},
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["imported"], 1)
        
        # Verify state exists in database
        self.assertTrue(StateRegion.objects.filter(code="BC", name="British Columbia").exists())
