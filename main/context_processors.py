from django.conf import settings

def capcha(request):
    return {'YACAPCHA_CLIENT': settings.YACAPCHA_CLIENT}
