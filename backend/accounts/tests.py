from rest_framework import status
from rest_framework.test import APITestCase

from django.contrib.auth import authenticate, get_user_model
from django.urls import reverse

User = get_user_model()


class UserRegistrationTests(APITestCase):
    def setUp(self):
        self.url = reverse("register")
        self.valid_data = {
            "email": "mehdi@example.com",
            "username": "mehdi",
            "password": "StrongPass123!@#",
            "password_confirmation": "StrongPass123!@#",
        }

    def test_register_user_successfully(self):
        response = self.client.post(
            self.url,
            self.valid_data,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username="mehdi").exists())

        user = User.objects.get(username="mehdi")
        self.assertTrue(user.check_password("StrongPass123!@#"))

    def test_register_with_duplicate_email(self):
        User.objects.create_user(
            username="another_user",
            email="mehdi@example.com",
            password="AnotherStrongPass123!@#",
        )

        response = self.client.post(
            self.url,
            self.valid_data,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_with_mismatched_passwords(self):
        data = self.valid_data.copy()
        data["password_confirmation"] = "DifferentPass123!@#"

        response = self.client.post(
            self.url,
            data,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(User.objects.filter(username="mehdi").exists())


class UserViewTests(APITestCase):
    def setUp(self):
        self.url = reverse("profile")
        self.user = User.objects.create_user(
            username="mehdi",
            email="mehdi@example.com",
            password="StrongPass123!@#",
        )

    def authenticate(self):
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_without_authentication(self):
        response = self.client.get(self.url)

        self.assertIn(
            response.status_code,
            [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN],
        )

    def test_retrieve_profile_successfully(self):
        self.authenticate()

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.user.id)
        self.assertEqual(response.data["email"], self.user.email)
        self.assertEqual(response.data["username"], self.user.username)

    def test_update_profile_successfully(self):
        self.authenticate()

        data = {
            "username": "new_username",
            "first_name": "Mehdi",
            "last_name": "Tester",
        }
        response = self.client.patch(
            self.url,
            data,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.user.refresh_from_db()
        self.assertEqual(self.user.username, "new_username")
        self.assertEqual(self.user.first_name, "Mehdi")
        self.assertEqual(self.user.last_name, "Tester")

    def test_update_profile_does_not_change_email(self):
        self.authenticate()

        data = {"email": "hacked@example.com"}
        response = self.client.patch(
            self.url,
            data,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.user.refresh_from_db()
        self.assertEqual(self.user.email, "mehdi@example.com")

    def test_user_cannot_change_is_staff_through_profile(self):
        self.authenticate()

        self.assertFalse(self.user.is_staff)

        data = {"is_staff": True}
        response = self.client.patch(
            self.url,
            data,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.user.refresh_from_db()
        self.assertFalse(self.user.is_staff)
        self.assertNotIn("is_staff", response.data)


class EmailBackendTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="mehdi",
            email="mehdi@example.com",
            password="StrongPass123!@#",
        )

    def test_authenticate_with_correct_credentials(self):
        user = authenticate(
            email="mehdi@example.com",
            password="StrongPass123!@#",
        )

        self.assertIsNotNone(user)
        self.assertEqual(user.pk, self.user.pk)

    def test_authenticate_with_wrong_password(self):
        user = authenticate(
            email="mehdi@example.com",
            password="WrongPass123!@#",
        )

        self.assertIsNone(user)

    def test_authenticate_with_unknown_email(self):
        user = authenticate(
            email="unknown@example.com",
            password="StrongPass123!@#",
        )

        self.assertIsNone(user)


class LoginViewTests(APITestCase):
    def setUp(self):
        self.url = reverse("login")
        self.credentials = {
            "email": "mehdi@example.com",
            "password": "StrongPass123!@#",
        }
        self.user = User.objects.create_user(
            username="mehdi",
            email="mehdi@example.com",
            password="StrongPass123!@#",
        )

    def test_login_successfully_issues_tokens(self):
        response = self.client.post(
            self.url,
            self.credentials,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("refresh", response.data)
        self.assertIn("access", response.data)

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {response.data['access']}",
        )
        profile_response = self.client.get(reverse("profile"))

        self.assertEqual(profile_response.status_code, status.HTTP_200_OK)
        self.assertEqual(profile_response.data["email"], self.user.email)

    def test_login_with_wrong_password(self):
        data = self.credentials.copy()
        data["password"] = "WrongPass123!@#"

        response = self.client.post(
            self.url,
            data,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn("refresh", response.data)
        self.assertNotIn("access", response.data)

    def test_login_with_unknown_email(self):
        data = self.credentials.copy()
        data["email"] = "unknown@example.com"

        response = self.client.post(
            self.url,
            data,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn("refresh", response.data)
        self.assertNotIn("access", response.data)

    def test_login_with_inactive_user(self):
        self.user.is_active = False
        self.user.save()

        response = self.client.post(
            self.url,
            self.credentials,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn("refresh", response.data)
        self.assertNotIn("access", response.data)