import csv

from django.contrib import admin
from django.http import HttpResponse

from .models import *

admin.site.site_header = 'Panfcate'
admin.site.site_title = 'Panfcate'


def export_as_csv(self, request, queryset):

    meta = self.model._meta
    field_names = [field.name for field in meta.fields]
    field_rus_names = [field.verbose_name for field in meta.fields]

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename={}.csv'.format(meta)
    writer = csv.writer(response)

    writer.writerow(field_rus_names)
    for obj in queryset:
        writer.writerow([getattr(obj, field) for field in field_names])

    return response


export_as_csv.short_description = "Экспортировать в формат CSV"


def convert_bool(string: str) -> str:
    if string == "True":
        return "Да"
    elif string == "False":
        return "Нет"
    else:
        return string


def print(self, request, queryset):

    meta = self.model._meta
    field_names = [field.name for field in meta.fields]
    data = '<table id="result_list">'
    data += '<tr>'
    data += '<td>' + '</td><td>'.join([field.verbose_name for field in meta.fields]) + '</td>'
    data += '</tr>'
    for obj in queryset:
        data += '<tr>'
        data += '<td>' + '</td><td>'.join(convert_bool(str(getattr(obj, field))) for field in field_names) + '</td>'
        data += '</tr>'
    data += '</table>'

    content = '''
    <script type="text/javascript">
		  var newWin=window.open('','Print');
		  newWin.document.open();
		  newWin.document.write('<html><body onload="window.print()"><style> #result_list {border:1px solid #000; border-collapse:collapse;} #result_list td, #result_list th {border:1px solid #000; border-collapse:collapse; padding:5px;} </style>''' + data + '''</body></html>');
		  newWin.document.close();
		  window.location = "''' + str(request.path) +  '''";
    </script>
    '''

    response = HttpResponse(content_type='text/html', content=content, charset='cp1251')

    return response


print.short_description = "Вывести на печать"


@admin.register(OrderStatus)
class OrderStatusAdmin(admin.ModelAdmin):
    # Список для отображения полей в админке
    list_display = ['order_status']
    # Сортировка
    ordering = ['order_status']
    # Список для поиска
    search_fields = ['order_status']

    # Добавление функций экспорта
    actions = [export_as_csv, print]


@admin.register(EventType)
class EventTypeAdmin(admin.ModelAdmin):
    # Список для отображения полей в админке
    list_display = ['event_type']
    # Сортировка
    ordering = ['event_type']
    # Список для поиска
    search_fields = ['event_type']
    # Добавление функций экспорта
    actions = [export_as_csv, print]


@admin.register(Cat)
class CatAdmin(admin.ModelAdmin):
    # Список для отображения полей в админке
    list_display = ['name_cat']
    # Сортировка
    ordering = ['name_cat']
    # Список для поиска
    search_fields = ['name_cat']
    # Добавление функций экспорта
    actions = [export_as_csv, print]


@admin.register(Dish)
class DishAdmin(admin.ModelAdmin):
    # Список для отображения полей в админке
    list_display = ['name_dish', 'cat', 'price_dish', 'total_weight', 'availible']
    # Сортировка
    ordering = ['name_dish', 'cat__name_cat', 'price_dish', 'total_weight', 'availible']
    # Список для поиска
    search_fields = ['name_dish', 'cat__name_cat', 'price_dish', 'total_weight', 'availible']
    # Список для фильтрации
    list_filter = ['cat__name_cat', 'availible']
    # Добавление функций экспорта
    actions = [export_as_csv, print]


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    # Список для отображения полей в админке
    list_display = ['fio_client', 'telephone_client', 'login_client']
    # Сортировка
    ordering = ['fio_client', 'telephone_client', 'login_client']
    # Список для поиска
    search_fields = ['fio_client', 'telephone_client', 'login_client']
    # Добавление функций экспорта
    actions = [export_as_csv, print]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    # Список для отображения полей в админке
    list_display = ['id', 'dt_order', 'order_number', 'status', 'client', 'dt_event', 'price_org']
    # Сортировка
    ordering = ['dt_order', 'order_number', 'status__order_status', 'client__fio_client', 'dt_event', 'price_org']
    # Список для поиска
    search_fields = ['dt_order', 'order_number', 'status__order_status', 'client__fio_client', 'dt_event', 'price_org']
    # Список для фильтрации
    list_filter = ['status']
    # Добавление функций экспорта
    actions = [export_as_csv, print]


@admin.register(DishInOrder)
class DishInOrderAdmin(admin.ModelAdmin):
    # Список для отображения полей в админке
    list_display = ['dish', 'order', 'cnt', 'get_price']
    # Сортировка
    ordering = ['dish__name_dish', 'order__order_number', 'cnt', 'dish__price_dish']
    # Список для поиска
    search_fields = ['dish__name_dish', 'order__order_number', 'cnt', 'dish__price_dish']
    # Список для фильтрации
    list_filter = ['order__id']

    # Добавление функций экспорта
    actions = [export_as_csv, print]

    def get_price(self, obj):
        return obj.dish.price_dish
    get_price.short_description = "Цена блюда" 
