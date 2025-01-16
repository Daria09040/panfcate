"""
URL configuration for catering project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

# Обработка ошибок
# 400 – невозможно обработать запрос
handler400 = 'main.views.error400'
# 403 – доступ запрещен;
handler403 = 'main.views.error403'
# 404 = не найдено
handler404 = 'main.views.error404'
# 500 – ошибка сервера;
handler500 = 'main.views.error500'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main.urls'))
]