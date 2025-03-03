import json

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.status import (
    HTTP_201_CREATED,
    HTTP_200_OK,
    HTTP_404_NOT_FOUND,
    HTTP_403_FORBIDDEN,
)
from rest_framework.test import APIClient

from book.models import Book
from borrowing.models import Borrowing
from payment.models import Payment


BORROWING_LIST_URL = reverse("borrowing:borrowings-list")

def parse_response(response):
    return json.loads(response.content.decode("utf-8"))


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
        self.data = {
            "expected_return_date": "2025-04-28",
            "book": 1
        }

    def test_create_borrowing(self):
        self.client.force_authenticate(self.user1)
        response = self.client.post(
            BORROWING_LIST_URL,
            self.data
        )
        self.assertEqual(response.status_code, HTTP_201_CREATED)
        self.assertEqual(Borrowing.objects.count(), 1)
        self.assertEqual(Borrowing.objects.last().user, self.user1)
        self.assertEqual(Book.objects.get(pk=1).inventory, 9)


    def test_borrowing_list_for_user(self):
        self.client.force_authenticate(self.user1)
        self.client.post(
            BORROWING_LIST_URL,
            self.data
        )

        self.client.force_authenticate(self.user2)
        self.client.post(
            BORROWING_LIST_URL,
            self.data
        )

        response = self.client.get(BORROWING_LIST_URL)
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(len(parse_response(response)), 1)

    def test_borrowing_with_filter_is_active(self):
        self.client.force_authenticate(self.user1)

        self.data = {
            "expected_return_date": "2025-04-28",
            "actual_return_date": "2025-03-03",
            "book": 1
        }

        self.client.post(
            BORROWING_LIST_URL,
            self.data
        )

        response = self.client.get(f"{BORROWING_LIST_URL}?is_active=false")

        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(len(parse_response(response)), 0)

        response = self.client.get(f"{BORROWING_LIST_URL}?is_active=true")
        self.assertEqual(len(parse_response(response)), 1)


    def test_retrieve_borrowing(self):
        self.client.force_authenticate(self.user1)
        self.client.post(
            BORROWING_LIST_URL,
            self.data
        )
        url = reverse(
            "borrowing:borrowings-detail",
            args=[Borrowing.objects.last().id]
        )

        response = self.client.get(url)
        parsed_data = parse_response(response)
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertIn("id", parsed_data)
        self.assertIn("book", parsed_data)
        self.assertIn("expected_return_date", parsed_data)
        self.assertIn("actual_return_date", parsed_data)
        self.assertIn("book", parsed_data)

    def test_retrieve_borrowing_access_for_other_user(self):
        self.client.force_authenticate(self.user1)
        self.client.post(
            BORROWING_LIST_URL,
            self.data
        )

        self.client.force_authenticate(self.user2)
        url = reverse(
            "borrowing:borrowings-detail",
            args=[Borrowing.objects.last().id]
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTP_403_FORBIDDEN)
        self.assertEqual(
            parse_response(response)["message"],
            "You can`t see this information"
        )

    def test_borrowing_return_for_other_user(self):
        self.client.force_authenticate(self.user1)
        self.client.post(
            BORROWING_LIST_URL,
            self.data
        )
        self.client.force_authenticate(self.user2)
        url = reverse(
            "borrowing:borrowings-return",
            args=[Borrowing.objects.last().id]
        )
        response = self.client.post(url)
        self.assertEqual(response.status_code, HTTP_403_FORBIDDEN)
        self.assertEqual(
            parse_response(response)["error"],
            "You can`t do this"
        )

    def test_borrowing_return(self):
        self.client.force_authenticate(self.user1)
        self.client.post(
            BORROWING_LIST_URL,
            self.data
        )
        url = reverse(
            "borrowing:borrowings-return",
            args=[Borrowing.objects.last().id]
        )
        response = self.client.post(url)
        parsed_data = parse_response(response)
        self.assertIn("message", parsed_data)
        self.assertIn("payment_url", parsed_data)
        self.assertIn("payment_type", parsed_data)
        self.assertIn("total_payment", parsed_data)

        payment = Payment.objects.last()
        payment.status = "paid"
        payment.save()

        self.assertIsNotNone(Borrowing.objects.last().actual_return_date)
        book = Book.objects.get(pk=Borrowing.objects.last().book.id)
        self.assertEqual(book.inventory, 10)

    def test_borrowing_return_again(self):
        self.client.force_authenticate(self.user1)
        self.client.post(
            BORROWING_LIST_URL,
            self.data
        )
        url = reverse(
            "borrowing:borrowings-return",
            args=[Borrowing.objects.last().id]
        )
        response = self.client.post(url)
        payment = Payment.objects.last()
        payment.status = "paid"
        payment.save()
        response = self.client.post(url)
        self.assertEqual(response.status_code, HTTP_404_NOT_FOUND)
        self.assertEqual(
            parse_response(response)["error"],
            "Book already returned"
        )


class TestBorrowingForAdmin(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.book1 = Book.objects.create(
            title="test1",
            author="test1",
            cover="Hard",
            inventory=10,
            daily_fee=10,
        )

        self.admin_user = get_user_model().objects.create_user(
            email="admin@test.com",
            password="testpassword",
            is_staff=True,
        )
        self.user1 = get_user_model().objects.create_user(
            email="user1@test.com",
            password="testpassword"
        )
        self.user2 = get_user_model().objects.create_user(
            email="user2@test.com",
            password="testpassword"
        )
        self.data = {
            "expected_return_date": "2025-04-28",
            "book": 1
        }

    def test_borrowing_list_for_admin(self):
        self.client.force_authenticate(self.user1)
        self.client.post(
            BORROWING_LIST_URL,
            self.data
        )

        self.client.force_authenticate(self.user2)
        self.client.post(
            BORROWING_LIST_URL,
            self.data
        )

        self.client.force_authenticate(self.admin_user)
        response = self.client.get(BORROWING_LIST_URL)
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(len(parse_response(response)), 2)

    def test_borrowing_list_with_filter_user_id(self):
        self.client.force_authenticate(self.user1)
        self.client.post(
            BORROWING_LIST_URL,
            self.data
        )

        self.client.force_authenticate(self.user2)
        self.client.post(
            BORROWING_LIST_URL,
            self.data
        )

        self.client.force_authenticate(self.admin_user)
        response = self.client.get(f"{BORROWING_LIST_URL}?user_id=3")

        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(len(parse_response(response)), 1)

    def test_borrowing_retrieve_other_user(self):
        self.client.force_authenticate(self.user1)
        self.client.post(
            BORROWING_LIST_URL,
            self.data
        )
        self.client.force_authenticate(self.admin_user)
        url = reverse(
            "borrowing:borrowings-detail",
            args=[Borrowing.objects.last().id]
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTP_200_OK)

