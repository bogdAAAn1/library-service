import os
import tempfile
from decimal import Decimal

import PIL
from PIL import Image
from django.contrib.auth import get_user_model
from django.db.models.signals import pre_save, post_save
from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from book.models import Book
from book.signals import new_book_available

BOOK_URL = reverse("book:book-list")


class UnauthenticatedUserTests(TestCase):
    def setUp(self):
        pre_save.disconnect(new_book_available, sender=Book)
        post_save.disconnect(new_book_available, sender=Book)
        super().setUp()

        self.client = APIClient()

        self.book = Book.objects.create(
            title="Internal Medicine: in 2 books. Book 1. Diseases of the "
                  "Cardiovascular and Respiratory Systems",
            author="Nestor Seredyuk, Ihor Vakalyuk, Roman Yatsyshyn",
            cover="Soft",
            inventory=1,
            daily_fee="1.32",
        )

    def test_can_view_list_of_books(self):
        res = self.client.get(BOOK_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_can_view_books_details(self):
        res = self.client.get(BOOK_URL + f"{self.book.id}/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_book_forbidden(self):
        payload = {
            "title": "Travelbook. Ukraine",
            "author": "Iryna Taranenko, Mariya Vorobyova, "
                      "Marta Leshak, Yuliia Kurova",
            "cover": "Hard",
            "inventory": 2,
            "daily_fee": "0.87",
        }

        res = self.client.post(BOOK_URL, payload)
        self.assertEqual(
            res.status_code, status.HTTP_401_UNAUTHORIZED
        )


class AuthenticatedUserTests(TestCase):
    def setUp(self):
        pre_save.disconnect(new_book_available, sender=Book)
        post_save.disconnect(new_book_available, sender=Book)
        super().setUp()

        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.com", password="test_password"
        )
        self.client.force_authenticate(user=self.user)

        self.book = Book.objects.create(
            title="Internal Medicine: in 2 books. Book 1. Diseases of "
                  "the Cardiovascular and Respiratory Systems",
            author="Nestor Seredyuk, Ihor Vakalyuk, Roman Yatsyshyn",
            cover="Soft",
            inventory=1,
            daily_fee="1.32",
        )

    def test_can_view_list_of_books(self):
        res = self.client.get(BOOK_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_can_view_books_details(self):
        res = self.client.get(BOOK_URL + f"{self.book.id}/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_change_book_details_forbidden(self):
        payload = {
            "daily_fee": "0.87",
        }

        res = self.client.patch(BOOK_URL + f"{self.book.id}/", payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminUserTests(TestCase):
    def setUp(self):
        pre_save.disconnect(new_book_available, sender=Book)
        post_save.disconnect(new_book_available, sender=Book)
        super().setUp()

        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="admin@test.com", password="admin_password", is_staff=True
        )
        self.client.force_authenticate(user=self.user)

        self.book = Book.objects.create(
            title="Internal Medicine: in 2 books. Book 1. Diseases of the "
                  "Cardiovascular and Respiratory Systems",
            author="Nestor Seredyuk, Ihor Vakalyuk, Roman Yatsyshyn",
            cover="Soft",
            inventory=1,
            daily_fee="1.32",
        )

    def test_can_view_list_of_books(self):
        res = self.client.get(BOOK_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_can_view_books_details(self):
        res = self.client.get(BOOK_URL + f"{self.book.id}/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_book_allowed(self):
        payload = {
            "title": "Travelbook. Ukraine",
            "author": "Iryna Taranenko, Mariya Vorobyova, "
                      "Marta Leshak, Yuliia Kurova",
            "cover": "Hard",
            "inventory": 2,
            "daily_fee": Decimal("0.87"),
        }

        res = self.client.post(BOOK_URL, payload)
        book = Book.objects.get(id=res.data["id"])

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        for key in payload:
            self.assertEqual(payload[key], getattr(book, key))

    def test_change_book_details_allowed(self):
        payload = {
            "daily_fee": Decimal("0.87"),
        }

        res = self.client.patch(BOOK_URL + f"{self.book.id}/", payload)
        book = Book.objects.get(id=self.book.id)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(
            res.data["daily_fee"], str(payload["daily_fee"])
        )
        self.assertEqual(book.daily_fee, payload["daily_fee"])

    def test_create_book_with_image_valid_data(self):
        image = PIL.Image.new("RGB", size=(1, 1))
        file = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
        image.save(file)

        with open(file.name, "rb") as f:
            data = {
                "title": "Test Book",
                "author": "Test Author",
                "cover": "Hard",
                "inventory": 5,
                "daily_fee": 2.50,
                "image": f
            }
            res = self.client.post(BOOK_URL, data=data, format="multipart")

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        new_book = Book.objects.get(title="Test Book")

        self.assertTrue(new_book.image.name)

        self.assertIn("image", res.data)
        self.assertTrue(res.data["image"].startswith("http"))

        file.close()
        os.remove(file.name)

    def test_create_book_with_image_invalid_data(self):
        file = tempfile.NamedTemporaryFile(
            mode="w+", suffix=".txt", delete=False
        )
        file.write("I am fake image")
        with open(file.name, "rb") as f:
            data = {
                "title": "Test Book",
                "author": "Test Author",
                "cover": "Hard",
                "inventory": 5,
                "daily_fee": 2.50,
                "image": f
            }
            res = self.client.post(BOOK_URL, data=data, format="multipart")

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertIn(
            "The submitted file is empty.", res.data["image"][0]
        )

        file.close()
        os.remove(file.name)
