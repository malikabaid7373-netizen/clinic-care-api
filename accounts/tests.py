from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


User = get_user_model()


class AuthenticationApiTests(APITestCase):
    def test_register_login_and_me(self):
        register_response = self.client.post(
            reverse("register"),
            {
                "fullName": "Portfolio Patient",
                "email": "patient@example.com",
                "password": "SecureClinic@123",
                "confirmPassword": "SecureClinic@123",
            },
            format="json",
        )

        self.assertEqual(register_response.status_code, status.HTTP_201_CREATED)
        self.assertIn("access", register_response.data)
        self.assertEqual(register_response.data["user"]["fullName"], "Portfolio Patient")

        login_response = self.client.post(
            reverse("login"),
            {
                "email": "patient@example.com",
                "password": "SecureClinic@123",
            },
            format="json",
        )

        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {login_response.data['access']}",
        )

        me_response = self.client.get(reverse("me"))
        self.assertEqual(me_response.status_code, status.HTTP_200_OK)
        self.assertEqual(me_response.data["email"], "patient@example.com")
