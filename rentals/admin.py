from django.contrib import admin

# Register your models here.
# rentals/admin.py
from django.contrib import admin, messages
from django import forms
from .models import Book, Rental
from .services import fetch_book_by_title
from decimal import Decimal

class RentalAdminForm(forms.ModelForm):
    book_title = forms.CharField(required=False, help_text="If book not in DB, provide a title to fetch details from OpenLibrary")

    class Meta:
        model = Rental
        fields = ["user", "book", "book_title", "start_date", "months_rented", "is_active"]

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ("title", "number_of_pages", "openlibrary_id", "created_at")
    search_fields = ("title", "openlibrary_id")

@admin.register(Rental)
class RentalAdmin(admin.ModelAdmin):
    form = RentalAdminForm
    list_display = ("user", "book", "months_rented", "total_fee", "is_active", "start_date")
    list_filter = ("is_active",)
    search_fields = ("user__username", "book__title")
    actions = ["prolong_selected"]

    def save_model(self, request, obj, form, change):
        # If admin provided a book_title on create, fetch from OpenLibrary
        book_title = form.cleaned_data.get("book_title")
        if not change and book_title and not obj.book:
            info = fetch_book_by_title(book_title)
            if info:
                book, created = Book.objects.get_or_create(
                    openlibrary_id=info.get("openlibrary_id"),
                    defaults={
                        "title": info.get("title"),
                        "number_of_pages": info.get("number_of_pages"),
                        "raw_data": info.get("raw"),
                    }
                )
                obj.book = book
        # compute fee before saving
        obj.total_fee = obj.compute_total_fee()
        super().save_model(request, obj, form, change)

    def prolong_selected(self, request, queryset):
        total_additional = Decimal("0.00")
        for rental in queryset:
            added = rental.prolong(extra_months=1)
            total_additional += added
        self.message_user(request, f"Prolonged {queryset.count()} rentals by 1 month. Total added charges: ${total_additional}", level=messages.SUCCESS)
    prolong_selected.short_description = "Prolong selected rentals by 1 month"
