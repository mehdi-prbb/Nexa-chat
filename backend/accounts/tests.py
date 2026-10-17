from rest_framework import status
from rest_framework.test import APITestCase

from django.contrib.auth import get_user_model
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
