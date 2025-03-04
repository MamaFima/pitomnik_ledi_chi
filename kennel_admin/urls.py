from django.contrib import admin
from django.urls import path
from django.urls import include

urlpatterns = [
    path('admin/', admin.site.urls),  # Подключаем админку Django
    path("users/", include("users.urls")),
]

