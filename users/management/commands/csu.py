from typing import Any
import getpass
from django.core.management import BaseCommand

from users.models import User


class Command(BaseCommand):
    def handle(self, *args: Any, **options: Any) -> str | None:
        # User.objects.all().delete()
        default_name = getpass.getuser()
        default_email = "admin@admin.ru"

        email = input(f"Введите email (по умолчанию {default_email}): ")
        first_name = input(f"Введите имя (по умолчанию {default_name}): ")
        last_name = input(f"Введите фамилию (по умолчанию {default_name}): ")
        pass1 = input("Введите пароль: ")
        if not pass1:
            print("Пароль не может быть пустым")
            return
        pass2 = input("Повторите пароль пароль: ")

        if pass1 != pass2:
            print("Пароли не совпадают.")
            return        
        if not email:
            email = default_email
        if not first_name:
            first_name = default_name
        if not last_name:
            last_name = default_name

        superuser = User.objects.create(
            email=email,
            first_name=first_name,
            last_name=last_name,
            is_staff=True,
            is_superuser=True,
        )

        superuser.set_password(pass1)
        superuser.save(update_fields=["password"])
        print("Суперпользователь создан.")
        print(f"email: {email}")
