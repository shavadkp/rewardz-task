from django.shortcuts import render

# Create your views here.
# rentals/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Rental, Book
from .serializers import RentalSerializer, BookSerializer

class RentalViewSet(viewsets.ModelViewSet):
    queryset = Rental.objects.select_related("book", "user").all()
    serializer_class = RentalSerializer

    @action(detail=True, methods=["post"], url_path="prolong")
    def prolong(self, request, pk=None):
        rental = self.get_object()
        months = int(request.data.get("months", 1))
        if months < 1:
            return Response({"detail": "months must be >= 1"}, status=status.HTTP_400_BAD_REQUEST)
        added = rental.prolong(extra_months=months)
        return Response({
            "rental_id": rental.id,
            "additional_charge": str(added),
            "total_fee": str(rental.total_fee),
            "months_rented": rental.months_rented
        }, status=status.HTTP_200_OK)

class BookViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer