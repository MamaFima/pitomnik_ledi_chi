import django
import os

from users.models import User
from asgiref.sync import sync_to_async  # Для корректной работы в асинхронном боте

# 📌 Функция для добавления пользователя
@sync_to_async
def add_user(user_id, username, full_name, phone=None, city=None):
    User.objects.get_or_create(
        user_id=user_id,
        defaults={
            'username': username,
            'full_name': full_name,
            'phone': phone,
            'city': city
        }
    )

# 📌 Функция для получения всех пользователей
@sync_to_async
def get_all_users():
    return list(User.objects.all())  # Оборачиваем в list(), чтобы избежать проблем с асинхронностью
