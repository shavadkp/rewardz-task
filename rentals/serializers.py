# rentals/serializers.py
from rest_framework import serializers
from .models import Book, Rental
from .services import fetch_book_by_title

class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ["id", "title", "openlibrary_id", "number_of_pages"]

class RentalSerializer(serializers.ModelSerializer):
    book = BookSerializer(read_only=True)
    book_id = serializers.PrimaryKeyRelatedField(queryset=Book.objects.all(), source="book", write_only=True, required=False)
    title = serializers.CharField(write_only=True, required=False, help_text="Book title to fetch from OpenLibrary if book_id not provided")

    class Meta:
        model = Rental
        fields = ["id", "user", "book", "book_id", "title", "start_date", "months_rented", "total_fee", "is_active"]
        read_only_fields = ["total_fee"]

    def create(self, validated_data):
        # allow providing book_id or title (which will fetch from OpenLibrary)
        book = validated_data.pop("book", None)
        title = validated_data.pop("title", None)
        if not book and title:
            info = fetch_book_by_title(title)
            if info:
                book, _ = Book.objects.get_or_create(
                    openlibrary_id=info.get("openlibrary_id"),
                    defaults={
                        "title": info.get("title"),
                        "number_of_pages": info.get("number_of_pages"),
                        "raw_data": info.get("raw"),
                    }
                )
        if not book:
            raise serializers.ValidationError({"book": "Provide book_id or title to fetch book details."})
        validated_data["book"] = book
        rental = Rental.objects.create(**validated_data)
        rental.total_fee = rental.compute_total_fee()
        rental.save(update_fields=["total_fee"])
        return rental
