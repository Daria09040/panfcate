import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Cat',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name_cat', models.CharField(max_length=255, verbose_name='Категория блюд')),
            ],
            options={
                'verbose_name': '3. Категория блюд',
                'verbose_name_plural': '3. Категории блюд',
            },
        ),
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fio_client', models.CharField(max_length=255, verbose_name='ФИО клиента')),
                ('telephone_client', models.CharField(max_length=120, verbose_name='Телефон клиента')),
                ('login_client', models.CharField(max_length=255, verbose_name='Логин (почта) клиента')),
                ('password_client', models.CharField(max_length=2048, verbose_name='Пароль')),
            ],
            options={
                'verbose_name': '5. Клиент',
                'verbose_name_plural': '5. Клиенты',
            },
        ),
        migrations.CreateModel(
            name='EventType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('event_type', models.CharField(max_length=255, verbose_name='Тип мероприятия')),
            ],
            options={
                'verbose_name': '1. Тип мероприятия',
                'verbose_name_plural': '1. Типы мероприятий',
            },
        ),
        migrations.CreateModel(
            name='OrderStatus',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_status', models.CharField(max_length=255, verbose_name='Статус заказа')),
            ],
            options={
                'verbose_name': '2. Статус заказа',
                'verbose_name_plural': '2. Статусы заказов',
            },
        ),
        migrations.CreateModel(
            name='Dish',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name_dish', models.CharField(max_length=255, verbose_name='Название блюда')),
                ('descr_dish', models.TextField(blank=True, null=True, verbose_name='Описание блюда')),
                ('price_dish', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Цена (руб.)')),
                ('total_weight', models.FloatField(blank=True, null=True, verbose_name='Общий вес (кг)')),
                ('photo_dish', models.ImageField(blank=True, null=True, upload_to='photos/', verbose_name='Фото')),
                ('availible', models.BooleanField(blank=True, null=True, verbose_name='Доступность')),
                ('cat', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.cat', verbose_name='Категория')),
            ],
            options={
                'verbose_name': '4. Блюдо',
                'verbose_name_plural': '4. Блюда',
            },
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dt_order', models.DateTimeField(blank=True, null=True, verbose_name='Дата заказа')),
                ('address_event', models.CharField(blank=True, max_length=255, null=True, verbose_name='Адрес мероприятия')),
                ('dt_event', models.DateTimeField(blank=True, null=True, verbose_name='Дата мероприятия')),
                ('desr_event', models.TextField(blank=True, null=True, verbose_name='Описание мероприятия')),
                ('price_org', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Стоимость заказа (руб.)')),
                ('order_number', models.CharField(blank=True, max_length=20, null=True, verbose_name='Номер заказа')),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.client', verbose_name='Клиент')),
                ('event_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.eventtype', verbose_name='Тип мероприятия')),
                ('status', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='main.orderstatus', verbose_name='Статус заказа')),
            ],
            options={
                'verbose_name': '6. Заказ',
                'verbose_name_plural': '6. Заказы',
            },
        ),
        migrations.CreateModel(
            name='DishInOrder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cnt', models.SmallIntegerField(blank=True, default=1, null=True, verbose_name='Кол-во')),
                ('dish', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.dish', verbose_name='Блюдо')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.order', verbose_name='Заказ')),
            ],
            options={
                'verbose_name': '7. Блюдо в заказе',
                'verbose_name_plural': '7. Блюда в заказах',
                'unique_together': {('dish', 'order')},
            },
        ),
    ]
