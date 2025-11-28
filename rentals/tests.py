from django.test import TestCase

# Create your tests here.
# rentals/tests.py
from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Book, Rental
from decimal import Decimal

User = get_user_model()

class RentalModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="student", password="pass")

    def test_fee_for_300_pages(self):
        book = Book.objects.create(title="Big Book", number_of_pages=300)
        r = Rental.objects.create(user=self.user, book=book, months_rented=1)
        self.assertEqual(r.compute_total_fee(), Decimal("0.00"))
        r.months_rented = 4
        self.assertEqual(r.compute_total_fee(), Decimal("9.00"))  # (4-1)*3.00

    def test_prolong_returns_additional(self):
        book = Book.objects.create(title="Small", number_of_pages=150)
        r = Rental.objects.create(user=self.user, book=book, months_rented=1)
        added = r.prolong(extra_months=2)  # now months_rented=3
        # per month = 1.5 -> extra months = 2 -> total = 3.00
        self.assertEqual(added, Decimal("3.00"))
        self.assertEqual(r.total_fee, Decimal("3.00"))
