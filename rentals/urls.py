
from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import RentalViewSet, BookViewSet

router = DefaultRouter()
router.register(r"rentals", RentalViewSet, basename="rental")
router.register(r"books", BookViewSet, basename="book")

urlpatterns = [
    path("", include(router.urls)),
]
