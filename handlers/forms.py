from aiogram import Router, types
from aiogram.types import Message
from users.models import PuppyRequest
from aiogram import Bot
from django.conf import settings
from asgiref.sync import sync_to_async
import json

router = Router()

# ✅ ID хозяйки питомника
OWNER_CHAT_ID = 183208176  # Укажи правильный ID

# ✅ Обработчик Webhook от Google Forms
@router.message(lambda msg: msg.text.startswith("{"))  # Проверяет JSON
async def handle_google_form(message: Message):
    try:
        # ✅ Парсим JSON из сообщения
        form_data = json.loads(message.text)

        # ✅ Сохраняем в БД (выполняем в отдельном потоке)
        await sync_to_async(PuppyRequest.objects.create)(
            name=form_data["name"],
            country=form_data["country"],
            city=form_data["city"],
            gender=form_data["gender"],
            coat_type=form_data["coat_type"],
            color=form_data["color"],
            adult_weight=form_data["adult_weight"],
            purpose=form_data["purpose"],
            temperament=form_data["temperament"],
            has_children=form_data["has_children"] == "Да",
            children_age=form_data["children_age"],
            has_pets=form_data["has_pets"] == "Да",
            pets_info=form_data["pets_info"],
            has_experience=form_data["has_experience"] == "Да",
            budget=form_data["budget"],
            delivery_needed=form_data["delivery_needed"] == "Да",
            phone=form_data["phone"],
        )

        # ✅ Отправляем хозяйке уведомление
        bot = Bot(token=settings.BOT_TOKEN)
        await bot.send_message(
            chat_id=OWNER_CHAT_ID,
            text=f"🐶 Новая анкета на щенка!\n\n"
                 f"👤 {form_data['name']}\n"
                 f"📍 {form_data['city']}, {form_data['country']}\n"
                 f"📞 {form_data['phone']}\n"
                 f"🎨 Окрас: {form_data['color']}\n"
                 f"⚖ Вес: {form_data['adult_weight']}\n"
                 f"💰 Бюджет: {form_data['budget']}\n"
                 f"🚚 Доставка: {'Да' if form_data['delivery_needed'] else 'Нет'}\n\n"
                 f"✍ {form_data['purpose']}\n"
        )

        await message.answer("✅ Анкета успешно сохранена и отправлена!")

    except Exception as e:
        await message.answer(f"❌ Ошибка обработки анкеты: {e}")

