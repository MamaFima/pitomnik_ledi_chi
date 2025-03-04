import requests
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from users.models import PuppyRequest
from config import BOT_TOKEN  # ✅ Импортируем токен из config.py

TELEGRAM_OWNER_ID = 183208176  # ✅ ID хозяйки питомника

@csrf_exempt  # ⛔ Отключаем CSRF-защиту для API-запросов
def puppy_request_api(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)  # 📌 Читаем JSON-данные из запроса
            print(f"📩 Получены данные анкеты: {data}")  # ➡️ Логируем данные

            # ✅ Сохраняем данные в БД
            puppy_request = PuppyRequest.objects.create(
                name=data.get("name"),
                country=data.get("country"),
                city=data.get("city"),
                gender=data.get("gender"),
                coat_type=data.get("coat_type"),
                color=data.get("color"),
                adult_weight=data.get("adult_weight"),
                purpose=data.get("purpose"),
                temperament=data.get("temperament"),
                has_children=data.get("has_children") == "Да",
                children_age=data.get("children_age", ""),
                has_pets=data.get("has_pets") == "Да",
                pets_info=data.get("pets_info", ""),
                has_experience=data.get("has_experience") == "Да",
                budget=data.get("budget"),
                delivery_needed=data.get("delivery_needed") == "Да",
                phone=data.get("phone"),
            )

            # ✅ Отправляем уведомление в Telegram
            send_puppy_request_to_telegram(puppy_request)

            return JsonResponse({"success": True, "message": "Анкета успешно сохранена!"})

        except Exception as e:
            print(f"❌ Ошибка при обработке анкеты: {e}")
            return JsonResponse({"success": False, "error": str(e)}, status=400)

    return JsonResponse({"success": False, "error": "Метод не разрешён"}, status=405)

def send_puppy_request_to_telegram(puppy_request: PuppyRequest):
    """📩 Отправка заявки в Telegram хозяйке питомника"""
    text = (
        f"🐶 Новая заявка на щенка!\n\n"
        f"👤 ФИО: {puppy_request.name}\n"
        f"🌍 Страна: {puppy_request.country}\n"
        f"🏙 Город: {puppy_request.city}\n"
        f"⚧ Пол щенка: {puppy_request.gender}\n"
        f"🦴 Тип шерсти: {puppy_request.coat_type}\n"
        f"🎨 Окрас: {puppy_request.color}\n"
        f"⚖ Ожидаемый вес: {puppy_request.adult_weight}\n"
        f"🎯 Цель приобретения: {puppy_request.purpose}\n"
        f"🎭 Темперамент: {puppy_request.temperament}\n"
        f"👶 Дети в семье: {'Да' if puppy_request.has_children else 'Нет'}\n"
        f"👶 Возраст детей: {puppy_request.children_age or 'Не указано'}\n"
        f"🐕 Другие питомцы: {'Да' if puppy_request.has_pets else 'Нет'}\n"
        f"🐾 Какие питомцы: {puppy_request.pets_info or 'Не указано'}\n"
        f"📖 Опыт общения с чихуахуа: {'Да' if puppy_request.has_experience else 'Нет'}\n"
        f"💰 Бюджет: {puppy_request.budget}\n"
        f"🚚 Нужна ли доставка: {'Да' if puppy_request.delivery_needed else 'Нет'}\n"
        f"📞 Контактный телефон: {puppy_request.phone or 'Не указан'}\n"
    )

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    response = requests.post(url, data={"chat_id": TELEGRAM_OWNER_ID, "text": text})

    if response.status_code == 200:
        print("✅ Уведомление в Telegram успешно отправлено!")
    else:
        print(f"❌ Ошибка отправки в Telegram: {response.text}")
