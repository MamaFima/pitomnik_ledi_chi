import asyncio
import asyncio
import datetime
from aiogram import Bot
from config import BOT_TOKEN, GOOGLE_CALENDAR_ID  # ✅ Импортируем ID календаря из конфига
from integrations.google_calendar import get_calendar_service

bot = Bot(token=BOT_TOKEN)


async def send_reminders():
    """Отправляет напоминания за 30 минут до встречи."""
    service = get_calendar_service()
    now = datetime.datetime.utcnow()

    events_result = service.events().list(
        calendarId=GOOGLE_CALENDAR_ID,  # ✅ Используем ID из config.py
        timeMin=now.isoformat() + "Z",
        timeMax=(now + datetime.timedelta(minutes=30)).isoformat() + "Z",
        singleEvents=True,
        orderBy="startTime"
    ).execute()

    for event in events_result.get("items", []):
        # Получаем номер телефона клиента из описания события
        phone_number = event.get("description", "").split(": ")[1] if ":" in event.get("description", "") else None

        if phone_number:
            await bot.send_message(phone_number, f"📢 Напоминание! Встреча в питомнике через 30 минут.")

