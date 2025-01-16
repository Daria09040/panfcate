from django.test import TestCase, Client
from django.urls import reverse
from .models import *
from django.utils.timezone import now, make_aware
from datetime import datetime

class RegisterViewTestCase(TestCase):
    def setUp(self):
        # Создание клиента для отправки запросов
        self.client = Client()
        self.register_url = reverse('register')
        self.valid_data = {
            'email': 'testuser@example.com',
            'password': 'securepassword',
            'fio': 'Тестовый Пользователь',
            'tel': '+79001234567'
        }
        self.invalid_data = {
            'email': '',  # Пустое поле для проверки обработки ошибок
            'password': '',
            'fio': '',
            'tel': ''
        }

    def test_register_success(self):
        # Тест успешной регистрации
        response = self.client.post(self.register_url, self.valid_data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Вы успешно зарегистрированы")  # Проверка сообщения
        self.assertTrue(Client.objects.filter(login_client='testuser@example.com').exists())

    def test_register_error(self):
        # Тест ошибки регистрации
        response = self.client.post(self.register_url, self.invalid_data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Ошибка регистрации")  # Проверка сообщения
        self.assertFalse(Client.objects.filter(login_client='').exists())

    def test_register_get_request(self):
        # Тест GET-запроса
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<form')  # Проверка наличия формы в HTML


class AddToCartViewTestCase(TestCase):
    def setUp(self):
        # Создание клиента и тестовые данные
        self.client = Client()
        self.add_to_cart_url = reverse('add_to_cart')
        self.dish = Dish.objects.create(
            name_dish='Тестовое блюдо',
            price_dish=500.00,
            photo_dish='test_photo.jpg',
            availible=True
        )

    def test_add_new_item_to_cart(self):
        # Добавление нового товара в корзину
        response = self.client.post(self.add_to_cart_url, {
            'dish_id': self.dish.id,
            'cnt': 2
        })

        # Проверка редиректа
        self.assertEqual(response.status_code, 302)

        # Проверка данных в сессии
        cart = self.client.session.get('cart', {})
        self.assertIn(str(self.dish.id), cart)
        self.assertEqual(cart[str(self.dish.id)]['quantity'], 2)
        self.assertEqual(cart[str(self.dish.id)]['name'], self.dish.name_dish)
        self.assertEqual(float(cart[str(self.dish.id)]['price']), self.dish.price_dish)

    def test_update_existing_item_in_cart(self):
        # Добавление товара в корзину
        session = self.client.session
        session['cart'] = {
            str(self.dish.id): {
                'dish_id': self.dish.id,
                'name': self.dish.name_dish,
                'price': str(self.dish.price_dish),
                'quantity': 1,
                'photo_dish': self.dish.photo_dish.url
            }
        }
        session.save()

        # Обновление количество товара
        response = self.client.post(self.add_to_cart_url, {
            'dish_id': self.dish.id,
            'cnt': 3
        })

        # Проверка редиректа
        self.assertEqual(response.status_code, 302)

        # Проверка обновленного количества
        cart = self.client.session.get('cart', {})
        self.assertIn(str(self.dish.id), cart)
        self.assertEqual(cart[str(self.dish.id)]['quantity'], 4)

    def test_add_to_cart_invalid_dish(self):
        # Попытка добавить несуществующий товар
        response = self.client.post(self.add_to_cart_url, {
            'dish_id': 999,
            'cnt': 1
        })

        # Проверка на возникновение исключения
        self.assertEqual(response.status_code, 500)

    def test_add_to_cart_invalid_quantity(self):
        # Попытка добавить товар с некорректным количеством
        response = self.client.post(self.add_to_cart_url, {
            'dish_id': self.dish.id,
            'cnt': -1
        })

        # Проверка на обработку ошибки
        self.assertEqual(response.status_code, 500)

    def test_get_request_to_add_to_cart(self):
        # GET-запрос к функции
        response = self.client.get(self.add_to_cart_url)

        # Проверка отклонения метода
        self.assertEqual(response.status_code, 405)


class MakeOrderViewTestCase(TestCase):
    def setUp(self):
        # Инициализация клиента и тестовых данных
        self.client = Client()
        self.make_order_url = reverse('make_order')  # Замените 'make_order' на правильный URL
        self.client_model = Client.objects.create(
            fio_client="Тест Клиент",
            telephone_client="1234567890",
            login_client="test@example.com",
            password_client="password123"
        )
        self.event_type = EventType.objects.create(name_event_type="Свадьба")
        self.dish = Dish.objects.create(
            name_dish="Тестовое блюдо",
            price_dish=500.00,
            photo_dish="test_photo.jpg",
            availible=True
        )
        self.session_data = {
            'client_id': self.client_model.id,
            'cart': {
                str(self.dish.id): {
                    'dish_id': self.dish.id,
                    'name': self.dish.name_dish,
                    'price': str(self.dish.price_dish),
                    'quantity': 2
                }
            },
            'total_price': 1000.00
        }

    def test_make_order_success(self):
        # Устанавка данных сессии
        session = self.client.session
        session.update(self.session_data)
        session.save()

        # Данные для POST-запроса
        post_data = {
            'address_event': 'Тестовый адрес',
            'dt_event': now().isoformat(),
            'event_type': self.event_type.id,
            'desr_event': 'Описание тестового события'
        }

        # Выполнение запроса
        response = self.client.post(self.make_order_url, post_data)

        # Проверка редиректа
        self.assertEqual(response.status_code, 302)

        # Проверка созданного заказа
        order = Order.objects.latest('id')
        self.assertEqual(order.client, self.client_model)
        self.assertEqual(order.address_event, post_data['address_event'])
        self.assertEqual(order.desr_event, post_data['desr_event'])
        self.assertEqual(order.price_org, self.session_data['total_price'])
        self.assertEqual(order.event_type, self.event_type)

        # Проверка созданных блюд в заказе
        dish_in_order = DishInOrder.objects.get(order=order)
        self.assertEqual(dish_in_order.dish, self.dish)
        self.assertEqual(dish_in_order.cnt, self.session_data['cart'][str(self.dish.id)]['quantity'])

        # Проверка очистки корзины и флага успеха
        session = self.client.session
        self.assertNotIn('cart', session)
        self.assertNotIn('total_price', session)
        self.assertTrue(session.get('success'))

    def test_make_order_empty_cart(self):
        # Установка пустой корзины в сессии
        session = self.client.session
        session['client_id'] = self.client_model.id
        session['cart'] = {}
        session.save()

        # Данные для POST-запроса
        post_data = {
            'address_event': 'Тестовый адрес',
            'dt_event': now().isoformat(),
            'event_type': self.event_type.id,
            'desr_event': 'Описание тестового события'
        }

        # Выполнение запроса
        response = self.client.post(self.make_order_url, post_data)

        # Проверка, что заказ не создан
        self.assertEqual(Order.objects.count(), 0)
        self.assertEqual(response.status_code, 302)

        # Проверка данных в сессии
        session = self.client.session
        self.assertFalse(session.get('success'))

    def test_make_order_invalid_date(self):
        # Установка данных сессии
        session = self.client.session
        session.update(self.session_data)
        session.save()

        # Некорректная дата
        post_data = {
            'address_event': 'Тестовый адрес',
            'dt_event': 'Некорректная дата',
            'event_type': self.event_type.id,
            'desr_event': 'Описание тестового события'
        }

        # Выполнение запроса
        response = self.client.post(self.make_order_url, post_data)

        # Проверка, что заказ не создан
        self.assertEqual(Order.objects.count(), 0)
        self.assertEqual(response.status_code, 500)

    def test_make_order_get_request(self):
        # GET-запрос к функции
        response = self.client.get(self.make_order_url)

        # Проверка отклонения метода
        self.assertEqual(response.status_code, 405)  