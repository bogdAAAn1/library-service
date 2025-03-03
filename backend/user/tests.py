from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.token_url = reverse("user:token_obtain_pair")
        self.create_user_url = reverse("user:register")
        self.me_url = reverse("user:manage")

    def test_create_valid_user_success(self):
        payload = {
            "email": "test@test.com",
            "password": "test123",
        }
        res = self.client.post(self.create_user_url, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(email=payload["email"])
        self.assertTrue(user.check_password(payload["password"]))
        self.assertNotIn("password", res.data)

    def test_create_token_for_user(self):
        payload = {
            "email": "test@test.com",
            "password": "test123",
        }
        create_user(**payload)

        res = self.client.post(self.token_url, payload)
        self.assertIn("access", res.data)
        self.assertIn("refresh", res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_invalid_credentials(self):
        create_user(email="test@test.com", password="test123")
        payload = {
            "email": "test@test.com",
            "password": "wrongpassword",
        }

        res = self.client.post(self.token_url, payload)

        self.assertNotIn("access", res.data)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_token_no_user(self):
        payload = {
            "email": "test@test.com",
            "password": "test123",
        }
        res = self.client.post(self.token_url, payload)
        self.assertNotIn("access", res.data)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_token_missing_field(self):
        res = self.client.post(
            self.token_url, {"email": "test@test.com", "password": ""}
        )
        self.assertNotIn("access", res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)


class PrivateUserApiTests(TestCase):

    def setUp(self):
        self.token_url = reverse("user:token_obtain_pair")
        self.me_url = reverse("user:manage")

        self.user = create_user(
            email="test@test.com",
            password="test123",
        )
        self.client = APIClient()
        res = self.client.post(
            self.token_url, {"email": "test@test.com", "password": "test123"}
        )
        self.access_token = res.data["access"]
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}"
        )

    def test_retrieve_profile_success(self):
        res = self.client.get(self.me_url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(
            res.data,
            {
                "id": self.user.id,
                "email": self.user.email,
                "is_staff": False,
            },
        )
