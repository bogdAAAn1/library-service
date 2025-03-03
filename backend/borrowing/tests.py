from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.status import (
    HTTP_201_CREATED,
    HTTP_401_UNAUTHORIZED,
    HTTP_200_OK,
    HTTP_403_FORBIDDEN,
)
from rest_framework.test import APIClient

from book.models import Book
from borrowing.models import Borrowing
from payment.models import Payment

BORROWING_LIST_URL = reverse("borrowing:borrowings-list")


class TestBorrowingForUser(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.book1 = Book.objects.create(
            title="test1",
            author="test1",
            cover="Hard",
            inventory=10,
            daily_fee=10,
        )
        self.book2 = Book.objects.create(
            title="test2",
            author="test2",
            cover="Hard",
            inventory=10,
            daily_fee=10,
        )
        self.user1 = get_user_model().objects.create_user(
            email="user1@test.com", password="testpassword"
        )
        self.user2 = get_user_model().objects.create_user(
            email="user2@test.com", password="testpassword"
        )

    def test_create_borrowing(self):
        self.client.force_authenticate(self.user1)
        data = {"expected_return_date": "2025-04-28", "book": 1}
        response = self.client.post(BORROWING_LIST_URL, data)
        self.assertEqual(response.status_code, HTTP_201_CREATED)
        self.assertEqual(Borrowing.objects.count(), 1)
        self.assertEqual(Payment.objects.count(), 1)

    def test_retrieve_borrowing(self):
        self.client.force_authenticate(self.user1)
        data = {"expected_return_date": "2025-04-28", "book": 1}
        self.client.post(BORROWING_LIST_URL, data)
        url = reverse(
            "borrowing:borrowings-detail",
            args=[Borrowing.objects.last().id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTP_200_OK)

    def test_retrieve_borrowing_access_for_other_user(self):
        data = {"expected_return_date": "2025-04-28", "book": 1}
        self.client.post(BORROWING_LIST_URL, data)
        self.client.force_authenticate(self.user2)
        url = reverse(
            "borrowing:borrowings-detail",
            args=[Borrowing.objects.last().id]
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.content,
            b'{"message":"You don`t have access to this borrowing"}'
        )


class TestBorrowingForAdmin(TestCase):
    def setUp(self):
        self.book1 = Book.objects.create(
            title="test1",
            author="test1",
            cover="Hard",
            inventory=10,
            daily_fee=10,
        )
        self.book2 = Book.objects.create(
            title="test2",
            author="test2",
            cover="Hard",
            inventory=10,
            daily_fee=10,
        )

        self.admin_user = get_user_model().objects.create_user(
            email="admin@test.com",
            password="testpassword",
            is_staff=True,
        )
