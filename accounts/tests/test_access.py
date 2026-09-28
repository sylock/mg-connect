from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from accounts.services import AccountDraft, LastManagerError, create_account, update_account

User = get_user_model()


@override_settings(ROOT_URLCONF="config.urls")
class AccessControlTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.manager = create_account(
            None,
            AccountDraft(
                username="manager1",
                password="pass-manager-1",
                display_name="Manager Un",
                is_manager=True,
            ),
        )
        self.employee = create_account(
            self.manager,
            AccountDraft(
                username="employee1",
                password="pass-employee-1",
                display_name="Employé Un",
                is_manager=False,
            ),
        )

    def test_anonymous_is_redirected_from_home(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("accounts:login"), response["Location"])

    def test_employee_can_view_team_reports_placeholder(self):
        self.client.login(username="employee1", password="pass-employee-1")
        response = self.client.get(reverse("reports"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Rapports")

    def test_employee_denied_user_management(self):
        self.client.login(username="employee1", password="pass-employee-1")
        response = self.client.get(reverse("accounts:user_list"))
        self.assertEqual(response.status_code, 403)

    def test_manager_can_open_user_management(self):
        self.client.login(username="manager1", password="pass-manager-1")
        response = self.client.get(reverse("accounts:user_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Comptes")

    def test_cannot_remove_last_manager(self):
        with self.assertRaises(LastManagerError):
            update_account(
                actor=self.manager,
                user=self.manager,
                display_name=self.manager.display_name,
                email="",
                is_salon_active=True,
                is_manager=False,
            )

    def test_second_manager_can_be_demoted_when_another_remains(self):
        second = create_account(
            self.manager,
            AccountDraft(
                username="manager2",
                password="pass-manager-2",
                display_name="Manager Deux",
                is_manager=True,
            ),
        )
        update_account(
            actor=self.manager,
            user=second,
            display_name=second.display_name,
            email="",
            is_salon_active=True,
            is_manager=False,
        )
        second.refresh_from_db()
        self.assertFalse(second.groups.filter(name="Manager").exists())

    def test_login_logout_flow(self):
        ok = self.client.login(username="employee1", password="pass-employee-1")
        self.assertTrue(ok)
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Accueil")
        self.client.post(reverse("accounts:logout"))
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 302)
