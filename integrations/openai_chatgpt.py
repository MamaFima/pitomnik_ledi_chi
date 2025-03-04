import requests
import asyncio
import datetime
from config import OPENAI_API_KEY, OPENAI_ASSISTANT_ID
from integrations.google_calendar import get_free_slots, schedule_appointment
from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

API_URL = "https://api.openai.com/v1"
HEADERS = {
    "Authorization": f"Bearer {OPENAI_API_KEY}",
    "Content-Type": "application/json",
    "OpenAI-Beta": "assistants=v2"
}

# FSM-состояние для выбора времени
class BookingState(StatesGroup):
    waiting_for_time = State()


async def ask_assistant(user_input, user_id, state: FSMContext = None):
    """
    Обрабатывает запрос пользователя: отправляет в OpenAI или предлагает кнопки.
    """
    user_input_lower = user_input.lower()

    # 🚀 Если пользователь хочет записаться в питомник
    if "запиши меня" in user_input_lower or "запись в питомник" in user_input_lower:
        print("📅 Пользователь хочет записаться. Проверяем доступные слоты...")

        today = datetime.datetime.now().date()
        free_slots = get_free_slots(today)

        if not free_slots:
            return "❌ На сегодня все записи заняты. Попробуйте выбрать другой день."

        # 💬 Бот предлагает выбрать время
        slot_buttons = [types.KeyboardButton(slot) for slot in free_slots]
        keyboard = types.ReplyKeyboardMarkup(
            keyboard=[slot_buttons[i : i + 2] for i in range(0, len(slot_buttons), 2)],
            resize_keyboard=True,
            one_time_keyboard=True
        )

        if state:
            await state.set_state(BookingState.waiting_for_time)
            await state.update_data(user_id=user_id)

        print("📅 Бот предложил выбрать время:", free_slots)
        return "📅 Выберите удобное время для записи:", keyboard

    # ✅ Если бот ЖДЁТ выбора времени
    if state and await state.get_state() == BookingState.waiting_for_time:
        user_data = await state.get_data()
        selected_time = user_input  # Время, которое выбрал пользователь
        await state.clear()  # Сбрасываем состояние

        # 🕒 Преобразуем выбранное время в datetime
        today = datetime.datetime.now().date()
        appointment_time = datetime.datetime.combine(today, datetime.datetime.strptime(selected_time, "%H:%M").time())

        # 📌 Записываем пользователя в Google Календарь
        result = schedule_appointment("Посетитель", f"UserID {user_data['user_id']}", appointment_time)

        return f"✅ Вы записаны на {selected_time}! {result}" if "http" in result else "⚠ Ошибка при записи."

    # 🐶 Вопросы про щенков – отправляем текст и кнопки в start.py
    # 🐶 Вопросы про щенков → предлагать конкретные кнопки
    if any(kw in user_input_lower for kw in ["щенки", "свободные щенки", "купить щенка", "завести щенка"]):
        return "🐶 У нас есть доступные щенки! Нажмите кнопку **'Свободные щенки'** или заполните анкету **'Хочу щенка'**."

        # 🛍 Вопросы про магазин → предлагать кнопку "Магазин"
    if any(kw in user_input_lower for kw in ["магазин", "товары", "купить корм", "товары для собак"]):
        return "🛍 Чтобы посмотреть ассортимент, нажмите кнопку **'Магазин'**."

        # 🏡 Вопросы про посещение питомника → предлагать кнопку "Посетить питомник"
    if any(kw in user_input_lower for kw in ["запись в питомник", "посетить питомник", "запиши меня"]):
        return "🏡 Запишитесь на посещение, нажав кнопку **'Посетить питомник'**."

    if any(kw in user_input_lower for kw in ["щенки", "свободные щенки", "купить щенка", "завести щенка"]):
        return "🐶 Вы можете посмотреть доступных щенков или оставить заявку, нажав на соответствующую кнопку ниже."

    # 🛍 Вопросы про магазин – отправляем текст и кнопки в start.py
    if any(kw in user_input_lower for kw in ["магазин", "товары", "купить корм", "товары для собак"]):
        return "🛍 Перейдите в наш магазин, нажав на кнопку ниже."

    # 🏡 Вопросы про посещение питомника – отправляем текст и кнопки в start.py
    if any(kw in user_input_lower for kw in ["запись в питомник", "посетить питомник", "запиши меня"]):
        return "🏡 Запишитесь на посещение питомника, нажав на кнопку ниже."

    # Если вопрос не связан с кнопками – отправляем в OpenAI
    return await send_to_openai(user_input)



async def send_to_openai(user_input):
    """
    Отправляет запрос в OpenAI и получает ответ.
    Если OpenAI не отвечает за 10 секунд, возвращает сообщение об ошибке.
    """
    try:
        API_URL = "https://api.openai.com/v1"
        HEADERS = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json",
            "OpenAI-Beta": "assistants=v2"
        }

        print("📡 Создаём тред для общения...")
        thread_response = requests.post(f"{API_URL}/threads", headers=HEADERS, json={}, timeout=10)

        if thread_response.status_code != 200:
            return "⚠ Ошибка: не удалось создать диалог с ассистентом."

        thread_id = thread_response.json().get("id")
        print(f"✅ Тред создан: {thread_id}")

        message_response = requests.post(
            f"{API_URL}/threads/{thread_id}/messages",
            headers=HEADERS,
            json={"role": "user", "content": user_input},
            timeout=10
        )

        if message_response.status_code != 200:
            return "⚠ Ошибка: не удалось отправить сообщение ассистенту."

        print("📡 Запускаем обработку...")
        run_response = requests.post(
            f"{API_URL}/threads/{thread_id}/runs",
            headers=HEADERS,
            json={"assistant_id": OPENAI_ASSISTANT_ID},
            timeout=10
        )

        if run_response.status_code != 200:
            return "⚠ Ошибка: ассистент не смог обработать запрос."

        run_id = run_response.json().get("id")
        print(f"✅ Запуск создан: {run_id}")

        # 🔄 Ожидание ответа (максимум 10 секунд)
        for _ in range(5):
            print("⌛ Ожидание ответа...")
            await asyncio.sleep(2)

            status_response = requests.get(
                f"{API_URL}/threads/{thread_id}/runs/{run_id}",
                headers=HEADERS,
                timeout=5
            )

            if status_response.status_code == 200:
                run_status = status_response.json().get("status")
                if run_status == "completed":
                    break
                elif run_status == "incomplete":
                    print("⚠ OpenAI не завершил обработку вовремя. Пробуем снова.")
                    continue

        messages_response = requests.get(f"{API_URL}/threads/{thread_id}/messages", headers=HEADERS, timeout=10)

        if messages_response.status_code != 200:
            return "⚠ Ошибка: не удалось получить ответ от ассистента."

        messages = messages_response.json().get("data", [])
        if not messages:
            return "⚠ Ошибка: ассистент не дал ответа."

        # 🔍 Ищем ПЕРВОЕ сообщение от ассистента
        assistant_reply = ""
        for msg in messages:
            if msg["role"] == "assistant" and "content" in msg:
                for item in msg["content"]:
                    if item["type"] == "text":
                        assistant_reply += item["text"]["value"] + "\n"
                break  # Берём только первое сообщение от ассистента

        assistant_reply = assistant_reply.strip()
        if not assistant_reply:
            return "⚠ Ошибка: ассистент не дал понятного ответа."

        print(f"✅ Ответ ассистента: {assistant_reply}")
        return assistant_reply

    except requests.exceptions.Timeout:
        return "⚠ OpenAI отвечает слишком долго. Попробуйте позже."

    except Exception as e:
        print(f"❌ Ошибка запроса к OpenAI: {e}")
        return "⚠ Ошибка: ассистент временно недоступен."

