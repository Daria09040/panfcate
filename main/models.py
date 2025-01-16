from django.db import models
from django.contrib.auth.models import User

def get_user_info(self):
    group_name = self.groups.all()[0].name if self.groups.exists() else "Без группы"
    return '{} {} [{}] {} ({})'.format(
        self.first_name, 
        self.last_name, 
        self.username, 
        self.email, 
        group_name
    )


User.add_to_class("__str__", get_user_info)


class EventType(models.Model):
    event_type = models.CharField(verbose_name="Тип мероприятия", max_length=255)

    def __str__(self):
        return f"{self.event_type}"

    class Meta:
        verbose_name = '1. Тип мероприятия'
        verbose_name_plural = '1. Типы мероприятий'


class OrderStatus(models.Model):
    order_status = models.CharField(verbose_name="Статус заказа", max_length=255)

    def __str__(self):
        return f"{self.order_status}"

    class Meta:
        verbose_name = '2. Статус заказа'
        verbose_name_plural = '2. Статусы заказов'


class Cat(models.Model):
    name_cat = models.CharField(verbose_name="Категория блюд", max_length=255)

    def __str__(self):
        return f"{self.name_cat}"

    class Meta:
        verbose_name = '3. Категория блюд'
        verbose_name_plural = '3. Категории блюд'

class Dish(models.Model):
    name_dish = models.CharField(verbose_name="Название блюда", max_length=255)
    descr_dish = models.TextField(verbose_name="Описание блюда", null=True, blank=True)
    price_dish = models.DecimalField(verbose_name="Цена (руб.)", max_digits=10, decimal_places=2, null=True, blank=True)
    total_weight = models.FloatField(verbose_name="Общий вес (кг)", null=True, blank=True)
    photo_dish = models.ImageField(upload_to='photos/', verbose_name="Фото", blank=True, null=True)
    availible = models.BooleanField(verbose_name="Доступность", null=True, blank=True)
    cat = models.ForeignKey('Cat', verbose_name="Категория", on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.cat} -> {self.name_dish} ({self.price_dish} руб.)"

    class Meta:
        verbose_name = '4. Блюдо'
        verbose_name_plural = '4. Блюда'


class Client(models.Model):
    fio_client = models.CharField(verbose_name="ФИО клиента", max_length=255)
    telephone_client = models.CharField(verbose_name="Телефон клиента", max_length=120)
    login_client = models.CharField(verbose_name="Логин (почта) клиента", max_length=255)
    password_client = models.CharField(verbose_name="Пароль", max_length=2048)

    def __str__(self):
        return f"{self.fio_client} [{self.telephone_client}]"

    class Meta:
        verbose_name = '5. Клиент'
        verbose_name_plural = '5. Клиенты'


class Order(models.Model):
    dt_order = models.DateTimeField(verbose_name="Дата заказа", null=True, blank=True)
    client = models.ForeignKey(Client, verbose_name="Клиент", on_delete=models.CASCADE)
    address_event = models.CharField(verbose_name="Адрес мероприятия", max_length=255, null=True, blank=True)
    dt_event = models.DateTimeField(verbose_name="Дата мероприятия", null=True, blank=True)
    desr_event = models.TextField(verbose_name="Описание мероприятия", null=True, blank=True)
    event_type = models.ForeignKey(EventType, verbose_name="Тип мероприятия", on_delete=models.CASCADE)
    price_org = models.DecimalField(verbose_name="Стоимость заказа (руб.)", max_digits=10, decimal_places=2, null=True, blank=True)
    status = models.ForeignKey(OrderStatus, verbose_name="Статус заказа", default=1, on_delete=models.CASCADE)
    order_number = models.CharField(verbose_name="Номер заказа", max_length=20, null=True, blank=True)

    def __str__(self):
        return f"№ {self.id} от {self.dt_order}"

    class Meta:
        verbose_name = '6. Заказ'
        verbose_name_plural = '6. Заказы'


class DishInOrder(models.Model):
    dish = models.ForeignKey(Dish, verbose_name="Блюдо", on_delete=models.CASCADE)
    cnt = models.SmallIntegerField(verbose_name="Кол-во", null=True, default=1, blank=True)
    order = models.ForeignKey('Order', verbose_name="Заказ", on_delete=models.CASCADE)

    class Meta:
        unique_together = ('dish', 'order')
        verbose_name = '7. Блюдо в заказе'
        verbose_name_plural = '7. Блюда в заказах'


