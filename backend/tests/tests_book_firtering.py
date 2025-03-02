from decimal import Decimal

from django.contrib.auth import get_user_model
from django.db.models import Q
from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from book.models import Book
from book.serializers import BookSerializer

BOOK_URL = reverse("book:book-list")


class UnauthenticatedUserTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.book1 = Book.objects.create(
            title="Internal Medicine: in 2 books. Book 1. Diseases of the Cardiovascular and Respiratory Systems",
            author="Nestor Seredyuk, Ihor Vakalyuk, Roman Yatsyshyn",
            cover="Soft",
            inventory=1,
            daily_fee=Decimal("1.32"),
        )
        self.book2 = Book.objects.create(
            title="Internal Medicine. In 2 books. Book 2. Diseases of the Digestive System, Kidney, Rheumatic and Hematological Diseases",
            author="Nestor Seredyuk, Ihor Vakalyuk, Roman Yatsyshyn",
            cover="Soft",
            inventory=1,
            daily_fee=Decimal("1.32"),
        )
        self.book3 = Book.objects.create(
            title="Animal Farm",
            author="George Orwell",
            cover="Hard",
            inventory=12,
            daily_fee=Decimal("0.45"),
        )
        self.book4 = Book.objects.create(
            title="The Little Prince",
            author="Antoine de Saint-Exupery",
            cover="Hard",
            inventory=101,
            daily_fee=Decimal("0.55"),
        )

    def test_books_ordered_by_id_by_default(self):
        res = self.client.get(BOOK_URL)
        books = Book.objects.all().order_by("id")
        expected_result = BookSerializer(books, many=True).data
        self.assertEqual(expected_result, res.data)

    def test_order_books_by_daily_fee_descending(self):
        res = self.client.get(BOOK_URL + "?ordering=-daily_fee")
        books = Book.objects.all().order_by("-daily_fee")
        expected_result = BookSerializer(books, many=True).data
        self.assertEqual(expected_result, res.data)

    def test_search_books_with_search_parameters_title(self):
        res = self.client.get(BOOK_URL + "?search=The Little Prince")
        books = Book.objects.filter(title__icontains="The Little Prince")
        expected_result = BookSerializer(books, many=True).data
        self.assertEqual(expected_result, res.data)

        res = self.client.get(BOOK_URL + "?search=med")
        books = Book.objects.filter(title__icontains="med")
        expected_result = BookSerializer(books, many=True).data
        self.assertEqual(expected_result, res.data)

        res = self.client.get(BOOK_URL + "?search=Antoine")
        self.assertEqual([], res.data)

    def test_search_books_with_search_parameters_cover(self):
        res = self.client.get(BOOK_URL + "?search=hard")
        books = Book.objects.filter(cover__icontains="hard")
        expected_result = BookSerializer(books, many=True).data
        self.assertEqual(expected_result, res.data)

        res = self.client.get(BOOK_URL + "?search=paper")
        self.assertEqual([], res.data)

    def test_search_books_with_search_parameters_inventory(self):
        res = self.client.get(BOOK_URL + "?search=01")
        books = Book.objects.filter(inventory__icontains="01")
        expected_result = BookSerializer(books, many=True).data
        self.assertEqual(expected_result, res.data)

        res = self.client.get(BOOK_URL + "?search=22")
        self.assertEqual([], res.data)

    def test_search_books_with_search_parameters_mixed(self):
        res = self.client.get(BOOK_URL + "?search=2")
        self.assertEqual(3, len(res.data))

    def test_filter_books_with_custom_filter_id(self):
        res = self.client.get(BOOK_URL + "?id=1,3")
        books = Book.objects.filter(id__in=[1, 3])
        expected_result = BookSerializer(books, many=True).data

        self.assertEqual(expected_result, res.data)

    def test_filter_books_with_custom_filter_author(self):
        res = self.client.get(BOOK_URL + "?author=saint")
        books = Book.objects.filter(author__icontains="saint")
        expected_result = BookSerializer(books, many=True).data

        self.assertEqual(expected_result, res.data)

        res = self.client.get(BOOK_URL + "?author=saint,George Orwell")
        books = Book.objects.filter(
            Q(author__icontains="saint") | Q(author__icontains="George Orwell")
        )
        expected_result = BookSerializer(books, many=True).data
        self.assertEqual(expected_result, res.data)
        self.assertEqual(2, len(res.data))

    def test_filter_books_with_custom_filter_daily_fee(self):
        res = self.client.get(BOOK_URL + "?daily_fee=1.32")

        books = Book.objects.filter(daily_fee=1.32)
        expected_result = BookSerializer(books, many=True).data

        self.assertEqual(expected_result, res.data)
        self.assertEqual(2, len(res.data))

        res = self.client.get(BOOK_URL + "?daily_fee=32")
        self.assertEqual(0, len(res.data))

    def test_filter_books_with_custom_filter_min_and_max_daily_fee(self):
        Book.objects.all().delete()
        book1 = Book.objects.create(
            title="t1", author="a1", cover="Hard", inventory=10, daily_fee=1
        )
        book2 = Book.objects.create(
            title="t2", author="a2", cover="Hard", inventory=10, daily_fee=2
        )
        book3 = Book.objects.create(
            title="t3", author="a3", cover="Hard", inventory=10, daily_fee=3
        )
        book4 = Book.objects.create(
            title="t4", author="a4", cover="Hard", inventory=10, daily_fee=4
        )
        book5 = Book.objects.create(
            title="t5", author="a5", cover="Hard", inventory=10, daily_fee=5
        )
        book6 = Book.objects.create(
            title="t6", author="a6", cover="Hard", inventory=10, daily_fee=6
        )
        book7 = Book.objects.create(
            title="t7", author="a7", cover="Hard", inventory=10, daily_fee=7
        )

        res = self.client.get(BOOK_URL + "?min_fee=4")
        self.assertEqual(4, len(res.data))

        res = self.client.get(BOOK_URL + "?min_fee=3")
        self.assertEqual(5, len(res.data))

        res = self.client.get(BOOK_URL + "?max_fee=3")
        self.assertEqual(3, len(res.data))

        res = self.client.get(BOOK_URL + "?max_fee=10")
        self.assertEqual(7, len(res.data))

        res = self.client.get(BOOK_URL + "?min_fee=3&max_fee=5")
        self.assertEqual(3, len(res.data))

        res = self.client.get(BOOK_URL + "?min_fee=7&max_fee=15")
        self.assertEqual(1, len(res.data))

        res = self.client.get(BOOK_URL + "?min_fee=8&max_fee=15")
        self.assertEqual(0, len(res.data))

    def test_filter_books_with_custom_filter_all_together(self):
        res = self.client.get(BOOK_URL + "?id=1,3&author=seredyuk&min_fee=0.7")
        self.assertEqual(1, len(res.data))

    def test_pagination_works(self):
        res_all = self.client.get(BOOK_URL)

        books = Book.objects.all()
        books_data = BookSerializer(books, many=True).data

        self.assertEqual(res_all.data, books_data)

        res_page = self.client.get(BOOK_URL + "?limit=2")
        print(res_page)
        self.assertEqual(len(res_page.data["results"]), 2)


class AuthenticatedUserTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.com", password="test_password"
        )
        self.client.force_authenticate(user=self.user)

        self.book1 = Book.objects.create(
            title="Internal Medicine: in 2 books. Book 1. Diseases of the Cardiovascular and Respiratory Systems",
            author="Nestor Seredyuk, Ihor Vakalyuk, Roman Yatsyshyn",
            cover="Soft",
            inventory=1,
            daily_fee=Decimal("1.32"),
        )
        self.book2 = Book.objects.create(
            title="Internal Medicine. In 2 books. Book 2. Diseases of the Digestive System, Kidney, Rheumatic and Hematological Diseases",
            author="Nestor Seredyuk, Ihor Vakalyuk, Roman Yatsyshyn",
            cover="Soft",
            inventory=1,
            daily_fee=Decimal("1.32"),
        )

    def test_authenticated_user_can_order_books_by_ids_descending(self):
        res = self.client.get(BOOK_URL + "?ordering=-id")
        books = Book.objects.all().order_by("-id")
        expected_result = BookSerializer(books, many=True).data
        self.assertEqual(expected_result, res.data)


class AdminUserTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="admin@test.com", password="admin_password", is_staff=True
        )
        self.client.force_authenticate(user=self.user)

        self.book1 = Book.objects.create(
            title="Animal Farm",
            author="George Orwell",
            cover="Hard",
            inventory=12,
            daily_fee=Decimal("0.45"),
        )
        self.book2 = Book.objects.create(
            title="The Little Prince",
            author="Antoine de Saint-Exupery",
            cover="Hard",
            inventory=10,
            daily_fee=Decimal("0.55"),
        )

    def test_admin_can_order_books_by_title_ascending(self):
        res = self.client.get(BOOK_URL + "?ordering=title")
        books = Book.objects.all().order_by("title")
        expected_result = BookSerializer(books, many=True).data
        self.assertEqual(expected_result, res.data)

    def test_admin_can_order_books_by_title_descending(self):
        res = self.client.get(BOOK_URL + "?ordering=-title")
        books = Book.objects.all().order_by("-title")
        expected_result = BookSerializer(books, many=True).data
        self.assertEqual(expected_result, res.data)
