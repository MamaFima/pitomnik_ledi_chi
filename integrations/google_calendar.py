import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build
from config import GOOGLE_CREDENTIALS_FILE, GOOGLE_CALENDAR_ID

SCOPES = ["https://www.googleapis.com/auth/calendar"]


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

    # Определяем временные границы (UTC, так как Google API работает в UTC)
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

    # Получаем список уже забронированных временных слотов
    booked_times = []
    for event in events:
        event_start = event["start"].get("dateTime")
        if event_start:
            booked_times.append(event_start[11:16])  # Берём только HH:MM

    available_slots = []
    current_time = start_time

    while current_time < end_time:
        slot = (current_time + datetime.timedelta(hours=3)).strftime("%H:%M")  # +3 часа к UTC
        if slot not in booked_times:  # Если слот не занят, добавляем его
            available_slots.append(slot)
        current_time += datetime.timedelta(hours=1)

    return available_slots  # ✅ Возвращает список доступных слотов


def get_next_available_slots():
    """
    Проверяет ближайшие две недели и возвращает доступные слоты для записи в питомник.
    """
    today = datetime.date.today()
    available_slots = {}

    for day_offset in range(14):  # Проверяем 14 дней вперёд
        date = today + datetime.timedelta(days=day_offset)

        # Запись возможна только по ПТ (4), СБ (5), ВС (6)
        if date.weekday() not in [4, 5, 6]:
            continue

        slots = get_free_slots(date)
        if slots:
            available_slots[str(date)] = slots

    print(f"📆 Найдено {len(available_slots)} дней с доступными слотами.")
    return available_slots  # Возвращает словарь с датами и временем


def schedule_appointment(client_name, phone, date_time):
    """Записывает клиента в Google Calendar, добавляя ФИО и телефон."""
    print(f"📅 Запись: {client_name}, {phone}, {date_time}")  # Отладка

    if date_time.weekday() not in [4, 5, 6] or not (12 <= date_time.hour < 20):
        return "❌ Запись возможна только по пятницам, субботам и воскресеньям с 12:00 до 20:00 (МСК)."

    try:
        service = get_calendar_service()

        event = {
            "summary": f"Запись в питомник: {client_name}",
            "description": f"📞 Телефон: {phone}\n👤 Записан: {client_name}",
            "start": {"dateTime": date_time.isoformat(), "timeZone": "Europe/Moscow"},
            "end": {"dateTime": (date_time + datetime.timedelta(hours=1)).isoformat(), "timeZone": "Europe/Moscow"},
            "reminders": {"useDefault": False, "overrides": [{"method": "popup", "minutes": 30}]}
        }

        print("📡 Отправка в Google Calendar...")  # Отладка
        event = service.events().insert(calendarId=GOOGLE_CALENDAR_ID, body=event).execute()
        print(f"✅ Успешно записано! Ссылка: {event.get('htmlLink')}")  # Отладка
        return event.get("htmlLink")

    except Exception as e:
        print(f"⚠ Ошибка при записи в календарь: {e}")
        return f"❌ Ошибка: {e}"
