from django.db import models

# Create your models here.
# rentals/models.py
from django.conf import settings
from django.db import models
from django.utils import timezone
from decimal import Decimal, ROUND_HALF_UP
from django.utils.timezone import localdate


User = settings.AUTH_USER_MODEL

def money(value):
    return Decimal(value).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

class Book(models.Model):
    title = models.CharField(max_length=512)
    openlibrary_id = models.CharField(max_length=128, blank=True, null=True)
    number_of_pages = models.PositiveIntegerField(blank=True, null=True)
    raw_data = models.JSONField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        pages = self.number_of_pages if self.number_of_pages else "unknown pages"
        return f"{self.title} ({pages})"

class Rental(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="rentals")
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="rentals")
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField(blank=True, null=True)
    months_rented = models.PositiveIntegerField(default=1)  # 1 month = initial free month
    total_fee = models.DecimalField(max_digits=9, decimal_places=2, default=Decimal("0.00"))
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    start_date = models.DateField(default=localdate)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user} -> {self.book} ({'active' if self.is_active else 'inactive'})"

    def page_fee_per_month(self):
        pages = self.book.number_of_pages
        if not pages:
            return money(0)
        per_month = Decimal(pages) / Decimal(100)
        return money(per_month)

    def compute_total_fee(self):
        """
        First month free. For months > 1, per-month fee = pages / 100.
        """
        if self.months_rented <= 1:
            return money(0)
        extra_months = self.months_rented - 1
        per_month = self.page_fee_per_month()
        total = per_month * extra_months
        return money(total)

    def prolong(self, extra_months=1):
        """
        Extend rental by extra_months and update total_fee and end_date.
        Returns Decimal additional charge applied.
        """
        if extra_months < 1:
            return money(0)
        before = self.compute_total_fee()
        self.months_rented += extra_months
        after = self.compute_total_fee()
        additional = after - before
        self.total_fee = after

        # Simple end_date calculation: start_date + 30 * months_rented days
        self.end_date = self.start_date + timezone.timedelta(days=30 * self.months_rented)
        self.save(update_fields=["months_rented", "total_fee", "end_date"])
        return money(additional)
