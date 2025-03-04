from aiogram import Router
from aiogram.types import Message
from integrations.google_calendar import schedule_appointment
import datetime

router = Router()

@router.message(commands=["schedule"])
async def schedule_command(message: Message):
    try:
        start_time = datetime.datetime.now() + datetime.timedelta(days=1, hours=10)  # Завтра в 10:00
        end_time = start_time + datetime.timedelta(hours=1)  # На 1 час
        summary = "Встреча в питомнике"
        description = f"Пользователь Telegram: {message.from_user.full_name}"

        schedule_appointment("your_calendar_id@group.calendar.google.com", start_time, end_time, summary, description)
        await message.answer("✅ Встреча успешно добавлена в календарь!")
    except Exception as e:
        await message.answer(f"❌ Не удалось записать встречу: {e}")
