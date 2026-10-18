from django.conf import settings


def site_globals(request):
    return {
        'CURRENCY_SYMBOL': getattr(settings, 'CURRENCY_SYMBOL', '₹'),
        'SITE_NAME': getattr(settings, 'SITE_NAME', 'SpendWise'),
    }