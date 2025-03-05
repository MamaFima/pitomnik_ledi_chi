import requests
from django.contrib import admin, messages
from django import forms
from django.shortcuts import render
from django.http import HttpResponseRedirect
from .models import User
from config import BOT_TOKEN
import logging
from django.contrib import admin
from .models import PuppyRequest  # ✅ Добавляем импорт
from users.models import VisitorAppointment


logger = logging.getLogger(__name__)  # ✅ Логгер

# ✅ URL Telegram API
TELEGRAM_API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

# ✅ Форма для ввода текста рассылки
class BroadcastForm(forms.Form):
    message = forms.CharField(widget=forms.Textarea, label="Текст рассылки")

# ✅ Функция рассылки сообщений через Telegram API
@admin.action(description="📢 Отправить персонализированную рассылку")
def send_broadcast(modeladmin, request, queryset):
    logger.info("📢 send_broadcast() вызвана!")
    print("📢 send_broadcast() вызвана!")  # 🔥 Лог в консоль

    # ✅ Добавляем явную проверку метода запроса
    if request.method == "POST":
        form = BroadcastForm(request.POST)

        if form.is_valid():
            print(f"✅ Форма валидна! Данные: {form.cleaned_data}")  # 🔥 Логируем полученные данные

            message_text = form.cleaned_data["message"]
            success_count = 0
            error_count = 0

            print(f"🔍 Найдено пользователей: {queryset.count()}")  # 🔥 Проверка пользователей

            for user in queryset:
                print(f"🟢 Обрабатываем пользователя: {user.user_id}")  # 🔥 Лог в консоль

                if user.user_id:
                    try:
                        personalized_message = f"👋 {user.full_name or 'Уважаемый клиент'}, {message_text}"
                        print(f"📨 Отправляем сообщение пользователю {user.user_id}: {personalized_message}")  # 🔥 Лог

                        response = requests.post(
                            TELEGRAM_API_URL,
                            json={"chat_id": user.user_id, "text": personalized_message}
                        )

                        response_data = response.json()
                        print(f"✅ Ответ от Telegram API: {response_data}")  # 🔥 Лог API-ответа

                        if response_data.get("ok"):
                            success_count += 1
                        else:
                            error_count += 1

                    except Exception as e:
                        print(f"❌ Ошибка отправки {user.user_id}: {e}")  # 🔥 Лог ошибки
                        error_count += 1

            print(f"✅ Итог: Успешно отправлено: {success_count}, Ошибок: {error_count}")  # 🔥 Лог итогов

            modeladmin.message_user(
                request,
                f"✅ Успешно отправлено: {success_count}, Ошибок: {error_count}",
                messages.SUCCESS,
            )
            return HttpResponseRedirect(request.get_full_path())

        else:
            print("❌ Форма невалидна!")  # 🔥 Лог, если форма не прошла валидацию
    else:
        print("⚠️ Запрос НЕ POST, открываем форму!")  # 🔥 Лог запроса
    print(f"📡 Данные из POST-запроса: {request.POST}")

    logger.info(f"📡 Данные из POST-запроса: {request.POST}")  # ➕ Отладка запроса
    form = BroadcastForm(request.POST)

    if not form.is_valid():
        logger.error(f"❌ Форма невалидна! Ошибки: {form.errors}")  # ➕ Покажет ошибки
        return render(request, "admin/broadcast_form.html", {"form": form, "users": queryset})


# ✅ Регистрируем модель пользователей
class UserAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'username', 'full_name', 'phone', 'city')
    search_fields = ('username', 'full_name', 'phone', 'city')
    actions = [send_broadcast]

admin.site.register(User, UserAdmin)


# ✅ Фикс регистрации новых пользователей в БД
def register_user(user_id, username, full_name):
    """Добавляет пользователя в БД, если его там нет."""
    user, created = User.objects.get_or_create(user_id=user_id)
    if created:
        user.username = username
        user.full_name = full_name
        user.save()
        logger.info(f"✅ Новый пользователь добавлен: {user_id} ({full_name})")




@admin.register(PuppyRequest)
class PuppyRequestAdmin(admin.ModelAdmin):
    list_display = ("name", "phone", "city", "gender", "budget", "created_at")
    search_fields = ("name", "phone", "city")
    list_filter = ("gender", "coat_type", "has_children", "has_pets", "has_experience", "delivery_needed")

    fieldsets = (
        ("Личная информация", {"fields": ("name", "phone", "country", "city")}),
        ("Предпочтения по щенку", {"fields": ("gender", "coat_type", "color", "adult_weight", "temperament")}),
        ("Семейная информация", {"fields": ("has_children", "children_age", "has_pets", "pets_info", "has_experience")}),
        ("Дополнительные параметры", {"fields": ("purpose", "budget", "delivery_needed")}),
        ("Дата заявки", {"fields": ("created_at",)}),
    )
    readonly_fields = ("created_at",)  # Дата заявки недоступна для редактирования

@admin.register(VisitorAppointment)
class VisitorAppointmentAdmin(admin.ModelAdmin):
    list_display = ("full_name", "phone", "date", "time", "chat_id", "created_at")
    search_fields = ("full_name", "phone", "date")
    list_filter = ("date",)

    fieldsets = (
        ("Данные посетителя", {"fields": ("full_name", "phone", "chat_id")}),
        ("Информация о визите", {"fields": ("date", "time")}),
    )

    readonly_fields = ("date", "time")  # Дата и время недоступны для редактирования





