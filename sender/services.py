from django.core.cache import cache
from config import settings
from sender.models import Client, Mailing


def get_statistic():
    """Получает статистику для главной страницы"""

    mailings = Mailing.objects.all()
    statistic = {
        "mailings_count": mailings.count(),
        "mailings_active_count": mailings.exclude(status=Mailing.STOPPED).count(),
        "clients_count": Client.objects.all().values("email").distinct().count(),
    }

    return statistic


def get_statistic_from_cache():
    """Получает статистику для главной страницы из кеша"""

    if settings.CACHE_ENABLED:
        key = "main_statistic"
        statistic = cache.get(key)
        if statistic is None:
            statistic = get_statistic()
            cache.set(key, statistic)
    else:
        statistic = get_statistic()

    return statistic
