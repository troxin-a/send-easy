from django_ckeditor_5.fields import CKEditor5Field
from django.db import models


NULLABLE = {"blank": True, "null": True}


class Client(models.Model):
    name = models.CharField(verbose_name="Ф.И.О", max_length=150)
    email = models.EmailField(verbose_name="Email", max_length=150)
    comment = models.TextField(verbose_name="Комментарий", **NULLABLE)

    def __str__(self):
        return f"{self.email} ({self.name})"

    class Meta:
        verbose_name = "клиента"
        verbose_name_plural = "клиенты"
        ordering = ("pk",)


class Text(models.Model):
    title = models.CharField(verbose_name="Тема", max_length=150)
    body = CKEditor5Field(verbose_name="Сообщение", **NULLABLE)

    def __str__(self):
        return f"{self.title}"

    class Meta:
        verbose_name = "сообщение"
        verbose_name_plural = "сообщения"
        ordering = ("pk",)


class Mailing(models.Model):
    ONE_TIME = "O"
    DAY = "D"
    WEEK = "W"
    MONTH = "M"
    LAUNCH_FREQUENCY = {
        ONE_TIME: "Одноразовая",
        DAY: "Раз в день",
        WEEK: "Раз в неделю",
        MONTH: "Раз в месяц",
    }

    CREATED = "C"
    RUNING = "R"
    STOPPED = "S"
    MAILING_STATUS = {
        CREATED: "Создана",
        RUNING: "Запущена",
        STOPPED: "Завершена",
    }


    name = models.CharField(verbose_name="Наименование", max_length=150, help_text="Введите наименование рассылки", **NULLABLE)
    started_at = models.DateTimeField(verbose_name="Время и дата", help_text="Введите время и дату первого запуска")
    periodicity = models.CharField(verbose_name="Периодичность", max_length=1, choices=LAUNCH_FREQUENCY, default=ONE_TIME, help_text="Выберите периодичность запуска")
    status = models.CharField(verbose_name="Статус", max_length=1, choices=MAILING_STATUS, default=CREATED, help_text="Выберите статус рассылки")
    clients = models.ManyToManyField(to=Client, verbose_name="Клиенты",  help_text="Выберите клиентов")
    text = models.ForeignKey(to=Text, verbose_name="Сообщение", on_delete=models.CASCADE, related_name="mailings", help_text="Выберите сообщение для рассылки")

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = "рассылку"
        verbose_name_plural = "рассылки"
        ordering = ("pk",)


class Attempt(models.Model):
    mailing = models.ForeignKey(to=Mailing, verbose_name="Рассылка", on_delete=models.DO_NOTHING, editable=False)
    started = models.DateTimeField(verbose_name="Дата и время запуска", auto_now=True, editable=False)
    status = models.BooleanField(verbose_name="Статус", default=True, editable=False)
    response_code = models.SmallIntegerField(verbose_name="Код ответа", editable=False)
    response_msg = models.CharField(verbose_name="Текст ответа сервера", max_length=250, editable=False, **NULLABLE)

    def __str__(self):
        return f"{self.started} | {self.mailing} | {self.status}"

    class Meta:
        verbose_name = "попытку"
        verbose_name_plural = "попытки"
        ordering = ("pk",)
