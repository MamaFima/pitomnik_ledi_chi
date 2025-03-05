import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build
from config import GOOGLE_CREDENTIALS_FILE, GOOGLE_CALENDAR_ID
from aiogram import Bot
from django.conf import settings
import asyncio
from users.models import VisitorAppointment  # ✅ Импорт модели для сохранения данных

SCOPES = ["https://www.googleapis.com/auth/calendar"]
KENNEL_ADDRESS = "Москва, Путевой проезд, 52"
KENNEL_PHONE = "+7 (916) 010-05-57"


def get_calendar_service():
    """Подключение к Google Calendar API."""
    credentials = service_account.Credentials.from_service_account_file(
        GOOGLE_CREDENTIALS_FILE, scopes=SCOPES
    )
    service = build("calendar", "v3", credentials=credentials)
    return service


def get_free_slots(date):
    """Получает свободные слоты на указанный день (ПТ, СБ, ВС с 12:00 до 20:00 МСК), исключая занятые."""
    if date.weekday() not in [4, 5, 6]:  # Только ПТ (4), СБ (5), ВС (6)
        return []

    service = get_calendar_service()

    start_time = datetime.datetime.combine(date, datetime.time(9, 0))  # 12:00 МСК (UTC+3)
    end_time = datetime.datetime.combine(date, datetime.time(17, 0))  # 20:00 МСК (UTC+3)

    events_result = service.events().list(
        calendarId=GOOGLE_CALENDAR_ID,
        timeMin=start_time.isoformat() + "Z",
        timeMax=end_time.isoformat() + "Z",
        singleEvents=True,
        orderBy="startTime",
    ).execute()

    events = events_result.get("items", [])
    booked_times = [event["start"]["dateTime"][11:16] for event in events if "dateTime" in event["start"]]

    available_slots = []
    current_time = start_time

    while current_time < end_time:
        slot = (current_time + datetime.timedelta(hours=3)).strftime("%H:%M")
        if slot not in booked_times:
            available_slots.append(slot)
        current_time += datetime.timedelta(hours=1)

    return available_slots


def get_next_available_slots():
    """Проверяет ближайшие две недели и возвращает доступные слоты."""
    today = datetime.date.today()
    available_slots = {}

    for day_offset in range(14):
        date = today + datetime.timedelta(days=day_offset)

        if date.weekday() not in [4, 5, 6]:
            continue

        slots = get_free_slots(date)
        if slots:
            available_slots[str(date)] = slots

    return available_slots


async def send_reminder(chat_id, text):
    """Отправка напоминания в Telegram."""
    bot = Bot(token=settings.BOT_TOKEN)
    try:
        await bot.send_message(chat_id=chat_id, text=text)
        print(f"✅ Напоминание отправлено {chat_id}: {text}")
    except Exception as e:
        print(f"❌ Ошибка отправки напоминания {chat_id}: {e}")


def schedule_appointment(client_name, phone, date_time, chat_id=None):
    """Записывает клиента в Google Calendar и сохраняет в БД."""
    print(f"📅 Запись: {client_name}, {phone}, {date_time}")

    if date_time.weekday() not in [4, 5, 6] or not (12 <= date_time.hour < 20):
        return "❌ Запись возможна только по пятницам, субботам и воскресеньям с 12:00 до 20:00 (МСК)."

    try:
        service = get_calendar_service()

        event = {
            "summary": f"Запись в питомник: {client_name}",
            "description": f"📞 Телефон: {phone}\n👤 Записан: {client_name}\nID: {chat_id or 'Не указан'}",
            "start": {"dateTime": date_time.isoformat(), "timeZone": "Europe/Moscow"},
            "end": {"dateTime": (date_time + datetime.timedelta(hours=1)).isoformat(), "timeZone": "Europe/Moscow"},
            "reminders": {"useDefault": False, "overrides": [{"method": "popup", "minutes": 30}]}
        }

        print("📡 Отправка в Google Calendar...")
        event = service.events().insert(calendarId=GOOGLE_CALENDAR_ID, body=event).execute()
        print(f"✅ Успешно записано! Ссылка: {event.get('htmlLink')}")

        # ✅ Сохраняем запись в БД
        VisitorAppointment.objects.create(
            full_name=client_name,
            phone=phone,
            date=date_time.date(),
            time=date_time.time(),
            chat_id=chat_id
        )

        return event.get("htmlLink")

    except Exception as e:
        print(f"⚠ Ошибка при записи в календарь: {e}")
        return f"❌ Ошибка: {e}"


def check_upcoming_appointments():
    """Проверяет, есть ли записи в питомник через 30 минут, и отправляет напоминания."""
    service = get_calendar_service()
    now = datetime.datetime.utcnow()
    reminder_time = now + datetime.timedelta(minutes=30)

    events_result = service.events().list(
        calendarId=GOOGLE_CALENDAR_ID,
        timeMin=now.isoformat() + "Z",
        timeMax=reminder_time.isoformat() + "Z",
        singleEvents=True,
        orderBy="startTime",
    ).execute()

    events = events_result.get("items", [])
    if not events:
        print("⏳ Нет записей на ближайшие 30 минут.")
        return

    for event in events:
        visitor_info = event.get("summary", "Посетитель")
        description = event.get("description", "Телефон: неизвестен")
        start_time = event["start"]["dateTime"][11:16]
        date = event["start"]["dateTime"][:10]

        # 📍 Получаем ID посетителя
        chat_id = None
        if "ID:" in description:
            chat_id = description.split("ID:")[-1].strip()

        # 📞 Получаем телефон из описания
        phone = "Неизвестен"
        if "📞 Телефон:" in description:
            phone = description.split("📞 Телефон:")[-1].split("\n")[0].strip()

        # 🏡 Уведомляем хозяйку питомника
        owner_message = (
            f"🏡 Напоминание! Через 30 минут ожидается визит:\n"
            f"👤 {visitor_info}\n📅 Дата: {date}, Время: {start_time}\n"
            f"📞 Телефон посетителя: {phone}\n"
            f"📍 Адрес питомника: {KENNEL_ADDRESS}\n📞 Телефон питомника: {KENNEL_PHONE}"
        )
        asyncio.run(send_reminder(183208176, owner_message))  # ID хозяйки

        # 📩 Отправляем посетителю
        if chat_id:
            visitor_message = (
                f"📢 Напоминание! Ваш визит в питомник 🏡 'Леди Чи' через 30 минут.\n"
                f"📅 Дата: {date}\n🕒 Время: {start_time}\n"
                f"📍 Адрес питомника: {KENNEL_ADDRESS}\n📞 Телефон питомника: {KENNEL_PHONE}\n"
                f"📌 Ждем вас!"
            )
            asyncio.run(send_reminder(chat_id, visitor_message))
