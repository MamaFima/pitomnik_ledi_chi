from django.db import models

class User(models.Model):
    user_id = models.BigIntegerField(unique=True)
    username = models.CharField(max_length=255, null=True, blank=True)
    full_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=15, null=True, blank=True)
    city = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.full_name

from django.db import models

class PuppyRequest(models.Model):
    name = models.CharField(max_length=255, verbose_name="ФИО")
    country = models.CharField(max_length=100, verbose_name="Страна")
    city = models.CharField(max_length=100, verbose_name="Город")
    gender = models.CharField(max_length=50, choices=[("Мальчик", "Мальчик"), ("Девочка", "Девочка")], verbose_name="Пол щенка")
    coat_type = models.CharField(max_length=100, choices=[("Длинношерстный", "Длинношерстный"), ("Гладкошерстный", "Гладкошерстный")], verbose_name="Тип шерсти")
    color = models.CharField(max_length=100, verbose_name="Желаемый окрас")
    adult_weight = models.CharField(max_length=50, verbose_name="Ожидаемый вес во взрослом возрасте")
    purpose = models.CharField(max_length=255, verbose_name="Цель приобретения собаки")
    temperament = models.CharField(max_length=255, verbose_name="Предпочтительный темперамент")
    has_children = models.BooleanField(verbose_name="Есть ли дети в семье?")
    children_age = models.CharField(max_length=255, blank=True, verbose_name="Возраст детей (если есть)")
    has_pets = models.BooleanField(verbose_name="Есть ли другие питомцы?")
    pets_info = models.TextField(blank=True, verbose_name="Какие питомцы (если есть)?")
    has_experience = models.BooleanField(verbose_name="Есть ли опыт общения с чихуахуа?")
    budget = models.CharField(max_length=100, verbose_name="Бюджет на приобретение щенка")
    delivery_needed = models.BooleanField(verbose_name="Нужна ли доставка в другой город/страну?")
    phone = models.CharField(max_length=20, verbose_name="Контактный телефон")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата заявки")

    def __str__(self):
        return f"Заявка от {self.name} ({self.phone})"

    class Meta:
        verbose_name = "Заявка на щенка"
        verbose_name_plural = "Заявки на щенков"
# Create your models here.
