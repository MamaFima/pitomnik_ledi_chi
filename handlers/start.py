from aiogram import Router, types
from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from datetime import datetime
from aiogram.filters import Command
from users.database import add_user
from integrations.google_calendar import schedule_appointment, get_next_available_slots, get_free_slots
from integrations.openai_chatgpt import ask_assistant
import logging
import re
logger = logging.getLogger(__name__)  # ✅ Теперь logger определён!

# 📌 Состояния записи в питомник
class BookingState(StatesGroup):
    waiting_for_datetime = State()
    waiting_for_name = State()
    waiting_for_phone = State()

logging.basicConfig(level=logging.INFO)
router = Router()

# 📌 Главное меню
def get_main_menu_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🐶 О породе чихуахуа"), KeyboardButton(text="🏡 О питомнике")],
            [KeyboardButton(text="🛒 Магазин"), KeyboardButton(text="🐾 Свободные щенки")],
            [KeyboardButton(text="💬 Задать вопрос"), KeyboardButton(text="❤️ Хочу щенка!")],
            [KeyboardButton(text="🏡 Посетить питомник")]
        ],
        resize_keyboard=True,
        input_field_placeholder="Выберите раздел 👇"
    )
    return keyboard

# 📌 Приветствие и регистрация пользователя
@router.message(Command("start"))
async def start_command(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username or "Не указан"
    full_name = message.from_user.full_name

    logger.info(f"📌 Новый пользователь зашел в бота: {user_id}, {username}, {full_name}")
    print(f"📌 Новый пользователь зашел в бота: {user_id}, {username}, {full_name}")
    print(f"🔍 add_user вызывается для: {user_id}, {username}, {full_name}")  # ✅ ОТЛАДКА

    await add_user(user_id, username, full_name)  # ✅ Добавляем `await`


    await message.answer(
        f"👋 Привет, {full_name}!\n"
        "Я бот питомника 🏡\n\n"
        "📌 Здесь ты можешь узнать о породе чихуахуа, питомнике, свободных щенках и нашем магазине.\n"
        "💬 Если у тебя есть вопросы, просто напиши мне!\n\n"
        "👇 Выбери раздел или задай вопрос:",
        reply_markup=get_main_menu_keyboard()
    )

# 📌 Обработчики кнопок ИИ-ассистента
@router.message(lambda msg: msg.text in ["🐶 О породе чихуахуа", "🏡 О питомнике", "💬 Задать вопрос"])
async def handle_ai_request(message: types.Message):
    response = await ask_assistant(message.text, message.from_user.id)
    await message.answer(response)

# 📌 Обработчик кнопки "Посетить питомник"
@router.message(lambda msg: msg.text == "🏡 Посетить питомник")
async def visit_kennel(message: types.Message):
    available_slots = get_next_available_slots()

    if not available_slots:
        await message.answer("❌ В ближайшие две недели нет доступных слотов. Попробуйте позже.")
        return

    response_text = "📅 Доступные дни и время для записи:\n\n"
    for date, slots in available_slots.items():
        response_text += f"🗓 {date}:\n" + "\n".join(f"- {slot}" for slot in slots) + "\n\n"

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="📅 Записаться", callback_data="book_appointment")]]
    )

    await message.answer(
        response_text + "Нажмите *Записаться*, чтобы выбрать удобное время.",
        parse_mode="Markdown",
        reply_markup=keyboard
    )


# 📌 Обработчик кнопки "Записаться"
@router.callback_query(lambda c: c.data == "book_appointment")
async def book_appointment(callback_query: CallbackQuery, state: FSMContext):
    """Начинаем процесс записи (ввод даты и времени)."""
    await callback_query.answer()  # Отвечаем, чтобы Telegram не завис
    await state.set_state(BookingState.waiting_for_datetime)

    await callback_query.message.answer(
        "📅 Пожалуйста, напишите дату и время в формате: *ДД.ММ.ГГГГ ЧЧ:ММ*\n"
        "Например: `14.03.2025 15:00`",
        parse_mode="Markdown"
    )


# 📌 Проверяем формат даты
DATE_TIME_PATTERN = r"^\d{2}\.\d{2}\.\d{4} \d{2}:\d{2}$"


@router.message(lambda msg: re.match(DATE_TIME_PATTERN, msg.text))
async def process_booking_request(message: types.Message, state: FSMContext):
    """Обрабатывает ввод даты, НЕ отправляя запрос в OpenAI."""
    try:
        user_input = message.text.strip()
        date_part, time_part = user_input.split(" ")

        formatted_date = datetime.strptime(date_part, "%d.%m.%Y").strftime("%Y-%m-%d")
        formatted_datetime = f"{formatted_date} {time_part}"

        available_slots = get_free_slots(datetime.strptime(formatted_date, "%Y-%m-%d").date())

        if time_part not in available_slots:
            await message.answer("❌ Это время уже занято. Выберите другое.")
            return

        await state.update_data(datetime=formatted_datetime)
        await state.set_state(BookingState.waiting_for_name)

        await message.answer("📝 Теперь введите ваше *ФИО* (например, Иванов Иван Иванович):", parse_mode="Markdown")

    except ValueError:
        await message.answer("❌ Ошибка: Неправильный формат даты. Введите в формате **ДД.ММ.ГГГГ ЧЧ:ММ**.")


# 📌 Запрос ФИО → Запрос телефона
@router.message(BookingState.waiting_for_name)
async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(BookingState.waiting_for_phone)
    await message.answer("📞 Теперь введите ваш *номер телефона* для связи (например, +7 900 123 45 67):",
                         parse_mode="Markdown")


# 📌 Запрос телефона → Запись в календарь
@router.message(BookingState.waiting_for_phone)
async def process_phone(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    name = user_data["name"]
    date_time = user_data["datetime"]
    phone = message.text.strip()

    phone_pattern = r"^\+?\d[\d\s\-\(\)]{9,14}$"
    if not re.match(phone_pattern, phone):
        await message.answer("❌ Ошибка: Некорректный формат телефона. Введите в формате *+7 900 123 45 67*.")
        return

    await state.clear()

    result = schedule_appointment(name, phone, datetime.strptime(date_time, "%Y-%m-%d %H:%M"))

    if "http" in result:
        await message.answer(f"✅ Вы успешно записаны на {date_time}!\n{result}")
    else:
        await message.answer("⚠ Ошибка при записи. Попробуйте другое время.")


# 📌 Кнопки "Магазин", "Свободные щенки", "Хочу щенка!"
@router.message(lambda msg: msg.text == "🛒 Магазин")
async def open_shop(message: types.Message):
    shop_link = "https://xn--d1abkal9e.xn--p1ai/shop"
    shop_button = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="Перейти в магазин 🛒", url=shop_link)]]
    )
    await message.answer("🛍 Добро пожаловать в наш магазин!", reply_markup=shop_button)

@router.message(lambda msg: msg.text == "🐾 Свободные щенки")
async def available_puppies(message: types.Message):
    puppies_link = "https://xn--d1abkal9e.xn--p1ai/pets"
    puppies_button = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="Посмотреть свободных щенков 🐾", url=puppies_link)]]
    )
    await message.answer("🐶 Здесь представлены все доступные щенки:", reply_markup=puppies_button)

@router.message(lambda msg: msg.text == "❤️ Хочу щенка!")
async def want_puppy(message: types.Message):
    from handlers.puppy_handler import handle_puppy_request
    await handle_puppy_request(message)

# 📌 Общий обработчик общения с ИИ
@router.message()
async def chat_with_ai(message: Message):
    """Если сообщение не похоже на дату, отправляем в OpenAI."""
    if not re.match(DATE_TIME_PATTERN, message.text):
        await message.answer("🤖 Думаю над ответом...")
        response = await ask_assistant(message.text, message.from_user.id)
        await message.answer(response)