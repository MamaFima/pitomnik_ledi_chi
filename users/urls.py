from django.urls import path
from .views import puppy_request_api  # Импортируем вьюху

urlpatterns = [
    path("api/puppy-request/", puppy_request_api, name="puppy_request_api"),
]
