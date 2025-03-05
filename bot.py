import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kennel_admin.settings')  # Подключаем настройки Django
django.setup()

from aiogram import Bot, Dispatcher
from handlers import start, ai_agent
from aiogram.types import BotCommand
from aiogram import types

from config import BOT_TOKEN  # Убедись, что в config.py есть BOT_TOKEN
from handlers import ai_agent  # ✅ Подключаем AI-обработчик
from handlers import start, forms  # Добавляем forms
import threading
from integrations.tasks import run_scheduler

# Запускаем фоновый процесс проверки записей
scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
scheduler_thread.start()


bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# 📌 Регистрация роутеров

dp.include_router(start.router)
dp.include_router(forms.router)  # Подключаем обработчик Webhook
dp.include_router(ai_agent.router)
async def set_commands():
    """Устанавливаем команды для бота"""
    commands = [
        BotCommand(command="start", description="Запустить бота"),
        BotCommand(command="reset", description="Обновить меню"),
    ]
    await bot.set_my_commands(commands)

async def main():
    """Запуск бота"""
    print("🤖 Бот запущен и готов к работе!")
    await set_commands()
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

