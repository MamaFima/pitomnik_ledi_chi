from aiogram import Router, types
from aiogram.types import Message
from integrations.openai_chatgpt import ask_assistant  # ✅ Используем готовую функцию

router = Router()

# 📌 Обработчик кнопок, которые должны работать с AI
@router.message(lambda msg: msg.text in ["🐶 О породе чихуахуа", "🏡 О питомнике", "💬 Задать вопрос"])
async def ai_buttons(message: Message):
    await message.answer("🤖 Думаю над ответом...")
    response = await ask_assistant(message.text)
    await message.answer(response)

# 📌 Общий обработчик AI для обычных сообщений
@router.message()
async def handle_ai_request(message: Message):
    user_text = message.text.strip()

    if user_text:
        await message.answer("🤖 Думаю над ответом...")
        response = await ask_assistant(user_text)
        await message.answer(response)
