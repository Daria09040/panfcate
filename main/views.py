import re
from datetime import datetime
from .models import *
from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import check_password
from django.shortcuts import render, redirect
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from django.utils.timezone import make_aware, now
from django.utils.html import escape
from django.contrib import messages
import requests
import json


def error400(request, exception):
    return render(request, 'main/400.html')


def error403(request, exception):
    return render(request, 'main/403.html')


def error404(request, exception):
    return render(request, 'main/404.html')


def error500(request, *args, **argv):
    return render(request, 'main/500.html')


def index(request):
    context = {'total_items': get_total_items(request)}
    return render(request, 'main/index.html', context)


def check_captcha(token, request):
    """Проверка токена Yandex.Captcha"""
    guest_ip = request.META.get('REMOTE_ADDR', '')
    response = requests.post(
        "https://smartcaptcha.yandexcloud.net/validate",
        params={
            "secret": settings.YACAPCHA_SERVER,
            "token": token,
            "ip": guest_ip,
        },
        timeout=1
    )
    if response.status_code != 200:
        return True
    return json.loads(response.text).get("status") == "ok"


def enter(request):
    if request.session.get('client_auth', False):
        return redirect('catalog')

    context = {'alert': None, 'total_items': get_total_items(request)}

    if request.method == 'POST':
        email = escape(request.POST.get('email', '').strip())
        password = escape(request.POST.get('password', '').strip())
        captcha_token = escape(request.POST.get('smart-token', ''))

        if not email or not password:
            context['alert'] = {'type': 'danger', 'message': 'Поля логина и пароля обязательны для заполнения.'}
            return render(request, 'main/enter.html', context)

        if not check_captcha(captcha_token, request):
            context['alert'] = {'type': 'danger', 'message': 'Проверка капчи не пройдена. Пожалуйста, попробуйте снова.'}
            return render(request, 'main/enter.html', context)

        try:
            client = Client.objects.get(login_client=email)
            if check_password(password, client.password_client):
                request.session['client_id'] = client.id
                request.session['client_fio'] = client.fio_client
                request.session['client_tel'] = client.telephone_client
                request.session['client_email'] = client.login_client
                request.session['client_auth'] = True
                return redirect('catalog')
            else:
                context['alert'] = {'type': 'danger', 'message': 'Неправильный логин или пароль.'}
        except Client.DoesNotExist:
            context['alert'] = {'type': 'danger', 'message': 'Неправильный логин или пароль.'}
        except Exception as e:
            context['alert'] = {'type': 'danger', 'message': str(e)}

    return render(request, 'main/enter.html', context)


def logout(request):
    if not request.session.get('client_auth', False):
        return redirect('enter')
    request.session.flush()
    return render(request, 'main/enter.html')


def validate_phone_number(phone):
    """
    Проверка номера телефона на соответствие российскому формату.
    Номер должен начинаться с +7 и содержать 11 цифр.
    """
    pattern = re.compile(r'^\+7\d{10}$')
    return pattern.match(phone)


def register(request):
    if request.session.get('client_auth', False):
        return redirect('catalog')

    context = {'alert': None, 'total_items': get_total_items(request)}

    if request.method == 'POST':
        email = escape(request.POST.get('email', '').strip())
        password = escape(request.POST.get('password', '').strip())
        fio = escape(request.POST.get('fio', '').strip())
        tel = escape(request.POST.get('tel', '').strip())
        captcha_token = escape(request.POST.get('smart-token', ''))

        MAX_EMAIL_LENGTH = 255
        MAX_FIO_LENGTH = 255
        MAX_PASSWORD_LENGTH = 2048
        MAX_PHONE_LENGTH = 15  

        missing_fields = []
        if not email:
            missing_fields.append("Email")
        if not password:
            missing_fields.append("Пароль")
        if not fio:
            missing_fields.append("Имя")
        if not tel:
            missing_fields.append("Телефон")

        if missing_fields:
            context['alert'] = {
                'type': 'danger',
                'message': f"Необходимо заполнить следующие поля: {', '.join(missing_fields)}."
            }
            return render(request, 'main/register.html', context)

        if len(email) > MAX_EMAIL_LENGTH:
            context['alert'] = {
                'type': 'danger',
                'message': f"Email слишком длинный. Максимальная длина: {MAX_EMAIL_LENGTH} символов."
            }
            return render(request, 'main/register.html', context)

        if len(fio) > MAX_FIO_LENGTH:
            context['alert'] = {
                'type': 'danger',
                'message': f"Имя слишком длинное. Максимальная длина: {MAX_FIO_LENGTH} символов."
            }
            return render(request, 'main/register.html', context)

        if len(password) > MAX_PASSWORD_LENGTH:
            context['alert'] = {
                'type': 'danger',
                'message': f"Пароль слишком длинный. Максимальная длина: {MAX_PASSWORD_LENGTH} символов."
            }
            return render(request, 'main/register.html', context)

        if len(tel) > MAX_PHONE_LENGTH:
            context['alert'] = {
                'type': 'danger',
                'message': f"Телефон слишком длинный. Максимальная длина: {MAX_PHONE_LENGTH} символов."
            }
            return render(request, 'main/register.html', context)

        try:
            validate_email(email)
        except ValidationError:
            context['alert'] = {
                'type': 'danger',
                'message': "Введите корректный адрес электронной почты."
            }
            return render(request, 'main/register.html', context)

        try:
            validate_password(password)
        except ValidationError as e:
            context['alert'] = {
                'type': 'danger',
                'message': f"Пароль не соответствует требованиям безопасности: {' '.join(e.messages)}"
            }
            return render(request, 'main/register.html', context)

        if not check_captcha(captcha_token, request):
            context['alert'] = {
                'type': 'danger',
                'message': 'Проверка капчи не пройдена. Пожалуйста, попробуйте снова.'
            }
            return render(request, 'main/register.html', context)

        hashed_password = make_password(password)

        try:
            Client.objects.create(
                fio_client=fio,
                telephone_client=tel,
                login_client=email,
                password_client=hashed_password 
            )
            context['alert'] = {
                'type': 'success',
                'message': 'Вы успешно зарегистрированы. <a href="enter">Войти</a>'
            }
        except Exception as e:
            context['alert'] = {
                'type': 'danger',
                'message': 'Произошла ошибка при регистрации. Попробуйте снова.'
            }

    return render(request, 'main/register.html', context)


def catalog(request):
    cart = request.session.get('cart', {})

    if request.method == 'POST':
        cat_id = request.POST.get('category', '').strip()
        if cat_id.isdigit(): 
            cat_id = int(cat_id)
            dishes = Dish.objects.filter(availible=True, cat__id=cat_id)
        else:
            cat_id = None
            dishes = Dish.objects.filter(availible=True)
    else:
        cat_id = None
        dishes = Dish.objects.filter(availible=True)

    categories = Cat.objects.order_by('name_cat')

    for dish in dishes:
        str_dish_id = str(dish.id)
        if str_dish_id in cart:
            dish.quantity = cart[str_dish_id]['quantity']
        else:
            dish.quantity = 0

    context = {
        'dishes': dishes,
        'categories': categories,
        'cat_id': cat_id,
        'total_items': get_total_items(request)
    }
    return render(request, 'main/catalog.html', context)


def dish(request):
    dish = Dish.objects.get(pk=request.GET.get('id', ''))
    context = {'dish': dish, 'total_items': get_total_items(request)}
    return render(request, 'main/dish.html', context)


def add_to_cart(request):
    if request.method == 'POST':
        dish_id = int(request.POST.get('dish_id', ''))
        cnt = int(request.POST.get('cnt', ''))
        
        if cnt < 1 or cnt > 100:
            messages.error(request, "Количество товара должно быть от 1 до 100")
            next_url = request.POST.get('next', 'cart')  
            return redirect(next_url)

        dish = Dish.objects.get(id=dish_id)
        cart = request.session.get('cart', {})

        if str(dish_id) in cart:
            cart[str(dish_id)]['quantity'] += cnt
        else:
            cart[str(dish_id)] = {'dish_id': dish.id, 'name': dish.name_dish, 'price': str(dish.price_dish), 'quantity': cnt, 'photo_dish': dish.photo_dish.url}

        request.session['cart'] = cart

        next_url = request.POST.get('next', 'cart') 
        if 'dish' in next_url:
            return redirect('cart') 

        return redirect(next_url)


def update_quantity(request):
    cart = request.session.get('cart', {})
    dish_id = request.POST.get('dish_id', '')
    quantity = int(request.POST.get('quantity', ''))

    if str(dish_id) in cart:
        current_quantity = cart[str(dish_id)]['quantity']
        new_quantity = current_quantity + quantity
        
        if new_quantity < 1:
            del cart[str(dish_id)]
        else:
            cart[str(dish_id)]['quantity'] = new_quantity

        request.session['cart'] = cart

    next_url = request.POST.get('next', 'cart') 
    return redirect(next_url)


def remove_from_cart(request):
    cart = request.session.get('cart', {})
    dish_id = request.POST.get('dish_id', '')
    if str(dish_id) in cart:
        del cart[str(dish_id)]
        request.session['cart'] = cart

    return redirect('cart')


def cart(request):
    MAX_ADDRESS_LENGTH = 255
    MAX_DESCRIPTION_LENGTH = 1024

    cart = request.session.get('cart', {})
    event_types = EventType.objects.order_by('event_type')
    total_price = sum(float(item['price']) * item['quantity'] for item in cart.values())
    request.session['total_price'] = total_price

    context = {
        'cart': cart,
        'total_price': total_price,
        'event_types': event_types,
        'alert': None,
        'success': request.session.pop('success', False),
        'order_number': None,
        'total_items': get_total_items(request)
    }

    if request.method == 'POST':
        try:
            if not request.session.get('client_auth', False):
                context['alert'] = {
                    'type': 'info',
                    'message': 'Для оформления заказа необходимо войти в аккаунт.',
                }
                return render(request, 'main/cart.html', context)

            address_event = escape(request.POST.get('address_event', '').strip())
            dt_event = escape(request.POST.get('dt_event', ''))
            event_type = escape(request.POST.get('event_type', '1'))
            desr_event = escape(request.POST.get('desr_event', '').strip())

            missing_fields = []
            if not address_event:
                missing_fields.append("Адрес мероприятия")
            if not dt_event:
                missing_fields.append("Время и дата мероприятия")
            if not event_type:
                missing_fields.append("Тип мероприятия")

            if missing_fields:
                context['alert'] = {
                    'type': 'danger',
                    'message': f"Необходимо заполнить следующие поля: {', '.join(missing_fields)}.",
                }
                return render(request, 'main/cart.html', context)

            if len(address_event) > MAX_ADDRESS_LENGTH:
                context['alert'] = {
                    'type': 'danger',
                    'message': f"Адрес мероприятия слишком длинный. Максимальная длина: {MAX_ADDRESS_LENGTH} символов.",
                }
                return render(request, 'main/cart.html', context)

            try:
                dt_event = make_aware(datetime.fromisoformat(dt_event))
            except ValueError:
                context['alert'] = {
                    'type': 'danger',
                    'message': "Некорректный формат даты/времени. Пожалуйста, используйте формат YYYY-MM-DDTHH:MM.",
                }
                return render(request, 'main/cart.html', context)

            if len(desr_event) > MAX_DESCRIPTION_LENGTH:
                context['alert'] = {
                    'type': 'danger',
                    'message': f"Описание мероприятия слишком длинное. Максимальная длина: {MAX_DESCRIPTION_LENGTH} символов.",
                }
                return render(request, 'main/cart.html', context)

            try:
                event_type = EventType.objects.get(id=int(event_type))
            except EventType.DoesNotExist:
                context['alert'] = {
                    'type': 'danger',
                    'message': "Неверный тип мероприятия.",
                }
                return render(request, 'main/cart.html', context)

            if not cart:
                context['alert'] = {
                    'type': 'danger',
                    'message': "Корзина пуста. Пожалуйста, добавьте блюда в корзину.",
                }
                return render(request, 'main/cart.html', context)

            order = Order.objects.create(
                dt_order=datetime.now(),
                client=Client.objects.get(id=request.session['client_id']),
                address_event=address_event,
                dt_event=dt_event,
                desr_event=desr_event,
                event_type=event_type,
                price_org=total_price,
            )

            for dish in cart:
                dish_obj = Dish.objects.get(id=int(cart[dish]['dish_id']))
                DishInOrder.objects.create(
                    order=order,
                    dish=dish_obj,
                    cnt=int(cart[dish]['quantity']),
                )

            del request.session['cart']
            del request.session['total_price']

            context['alert'] = {
                'type': 'success',
                'message': "Заказ успешно оформлен!",
            }
            context['order_number'] = order.id 
            context['total_items'] = get_total_items(request)
            
        except Exception as e:
            context['alert'] = {
                'type': 'danger',
                'message': 'Произошла ошибка при оформлении заказа. Попробуйте снова.',
            }

    return render(request, 'main/cart.html', context)


def orders(request):
    if not request.session.get('client_auth', False):
        return redirect('enter')
    orders = Order.objects.filter(client_id=request.session['client_id'])
    dishes_in_orders = {}
    for order in orders:
        order_id = order.id
        dishes_in_order = DishInOrder.objects.filter(order__id=order_id)
        dishes_in_orders[order_id] = dishes_in_order
    context = {'orders': orders, 'dishes_in_orders': dishes_in_orders, 'total_items': get_total_items(request)}
    print(dishes_in_orders)
    return render(request, 'main/orders.html', context)


def get_total_items(request):
    cart = request.session.get('cart', {})
    total_items = sum(item['quantity'] for item in cart.values())
    return total_items
