from django.contrib.auth.models import AbstractUser
from django.db import models

NULLABLE = {"blank": True, "null": True}


class User(AbstractUser):
    username = None
    email = models.EmailField(verbose_name="Почта", unique=True)
    token = models.CharField(max_length=16, **NULLABLE)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
