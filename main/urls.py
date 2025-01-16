from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('', views.index, name='index'),
    path('enter', views.enter, name='enter'),
    path('logout', views.logout, name='logout'),
    path('register', views.register, name='register'),
    path('catalog', views.catalog, name='catalog'),
    path('orders', views.orders, name='orders'),
    path('dish', views.dish, name='dish'),
    path('add_to_cart', views.add_to_cart, name='add_to_cart'),
    path('update_quantity', views.update_quantity, name='update_quantity'),
    path('cart', views.cart, name='cart'),
    path('cart/update_quantity', views.update_quantity, name='update_quantity'),
    path('cart/remove_from_cart', views.remove_from_cart, name='remove_from_cart'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
