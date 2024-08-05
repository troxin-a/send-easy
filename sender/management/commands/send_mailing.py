from django.core.management import BaseCommand

from sender.utils import send_mails


class Command(BaseCommand):
    """
    Запускает функцию рассылки
    """

    def handle(self, *args, **options):
        send_mails()
