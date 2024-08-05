import json
import os
from django.core.management import BaseCommand

from sender.models import Client
from config.settings import BASE_DIR


class Command(BaseCommand):

    @staticmethod
    def json_read_clients():
        with open(
            os.path.join(BASE_DIR, "fixtures", "sender", "clients.json"),
            encoding="UTF-8",
        ) as file:
            return json.load(file)

    def create_objects(self, model, read_json):
        objects_for_create = []

        # Обходим все значения категорий из фиктсуры для получения информации об одном объекте
        for obj in read_json():
            fields = {field: value for field, value in obj["fields"].items()}

            objects_for_create.append(model(**fields))

        # Создаем объекты в базе с помощью метода bulk_create()
        model.objects.bulk_create(objects_for_create)

    def handle(self, *args, **options):

        # Очищаем все таблицы
        Client.objects.all().delete()

        # Заполняем таблицы
        self.create_objects(Client, Command.json_read_clients)
