from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

TOKEN_URL = reverse("token_obtain_pair")
CREATE_USER_URL = reverse("register")
ME_URL = reverse("user_profile")


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user_success(self):
        payload = {
            "email": "test@test.com",
            "password": "test123",
            "first_name": "Test",
            "last_name": "User",
        }
        res = self.client.post(CREATE_USER_URL, payload)

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

        res = self.client.post(TOKEN_URL, payload)
        self.assertIn("access", res.data)
        self.assertIn("refresh", res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_invalid_credentials(self):
        create_user(email="test@test.com", password="test123")
        payload = {
            "email": "test@test.com",
            "password": "wrongpassword",
        }

        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn("access", res.data)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_token_no_user(self):
        payload = {
            "email": "test@test.com",
            "password": "test123",
        }
        res = self.client.post(TOKEN_URL, payload)
        self.assertNotIn("access", res.data)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_token_missing_field(self)
        res = self.client.post(TOKEN_URL, {"email": "test@test.com", "password": ""})
        self.assertNotIn("access", res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)


class PrivateUserApiTests(TestCase):

    def setUp(self):
        self.user = create_user(
            email="test@test.com",
            password="test123",
            first_name="Test",
            last_name="User",
        )
        self.client = APIClient()
        res = self.client.post(
            TOKEN_URL, {"email": "test@test.com", "password": "test123"}
        )
        self.access_token = res.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")

    def test_retrieve_profile_success(self):
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(
            res.data,
            {
                "id": self.user.id,
                "email": self.user.email,
                "first_name": self.user.first_name,
                "last_name": self.user.last_name,
                "tg_chat": self.user.tg_chat,
            },
        )

    def test_update_user_profile(self):
        payload = {"first_name": "NewName", "last_name": "NewLastName"}

        res = self.client.patch(ME_URL, payload)

        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, payload["first_name"])
        self.assertEqual(self.user.last_name, payload["last_name"])
        self.assertEqual(res.status_code, status.HTTP_200_OK)
