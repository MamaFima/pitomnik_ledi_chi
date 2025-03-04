from aiogram import types, Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from django.conf import settings
from django.db import IntegrityError
from asgiref.sync import async_to_sync
from users.models import PuppyRequest
from aiogram.utils.markdown import hbold

# Телеграм-аккаунт хозяйки питомника
OWNER_CHAT_ID = 183208176  # Заменить на реальный ID хозяйки

async def handle_puppy_request(message: types.Message):
    print(f"🐶 Обработчик 'Хочу щенка!' сработал для {message.from_user.id}")  # ➡️ Отладка
    print(f"📨 Отправка сообщения с анкетой пользователю {message.from_user.id}...")

    google_form_link = "https://forms.gle/YoVh3kjXgnZFXTmYA"
    form_button = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📝 Заполнить анкету", url=google_form_link)]
        ]
    )

    await message.answer(
        "Если Вы очень хотите приобрести маленького чихуахуа, но не можете определиться, какой именно щенок Вам лучше всего подойдет, "
        "мы с удовольствием поможем Вам. \n\n"
        "Для того, чтобы лучше понять Ваши потребности, заполните, пожалуйста, анкету.",
        reply_markup=form_button
    )

async def send_telegram_message(chat_id, text):
    """Отправка сообщения в Telegram"""
    bot = Bot(token=settings.BOT_TOKEN)
    try:
        await bot.send_message(chat_id=chat_id, text=text)
        print(f"✅ Успешно отправлено сообщение хозяйке ({chat_id})")
    except Exception as e:
        print(f"❌ Ошибка при отправке сообщения в Telegram: {e}")


def save_application_and_notify(data):
    print("📡 Попытка сохранить заявку в БД...")  # Проверяем, вызывается ли вообще
    try:
        application = PuppyRequest.objects.create(**data)
        print(f"✅ Заявка от {application.name} сохранена в БД!")  # Подтверждаем в терминале



        # Формируем сообщение
        message_text = (
            f"🐶 Новая анкета на щенка!\n\n"
            f"👤 {application.name}\n"
            f"📍 {application.city}, {application.country}\n"
            f"📞 {application.phone}\n"
            f"🎨 Окрас: {application.color}\n"
            f"⚖ Вес: {application.adult_weight}\n"
            f"💰 Бюджет: {application.budget}\n"
            f"🚚 Доставка: {'Да' if application.delivery_needed else 'Нет'}\n\n"
            f"✍ {application.purpose}\n"
        )

        print(f"📡 Отправляем сообщение в Telegram хозяйке {OWNER_CHAT_ID}")  # ➡️ Отладка
        async_to_sync(send_telegram_message)(OWNER_CHAT_ID, message_text)
        print("✅ Сообщение отправлено в Telegram!")  # ➡️ Отладка

        return True
    except Exception as e:
        print(f"❌ Ошибка при сохранении анкеты или отправке в Telegram: {e}")
        return False

