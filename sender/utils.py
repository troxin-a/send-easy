# import os
import smtplib
from django.utils.html import strip_tags
import pytz
import calendar
from datetime import datetime, timedelta
# from urllib.parse import urljoin

from django.conf import settings
# from django.core.files.storage import FileSystemStorage
from django.core.mail import EmailMultiAlternatives

from sender.models import Attempt, Mailing


# class CustomStorage(FileSystemStorage):
#     """Custom storage for django_ckeditor_5 images."""

#     location = os.path.join(settings.MEDIA_ROOT, "django_ckeditor_5")
#     base_url = urljoin(settings.MEDIA_URL, "django_ckeditor_5/")


class SendMailing:
    attempt = None

    def __init__(self, mailing: Mailing, current_datetime):
        self.mailing = mailing
        self.current_datetime = current_datetime
        self.period = self.__set_period()

    def __set_period(self) -> int:
        if self.mailing.periodicity == self.mailing.DAY:
            return 1
        elif self.mailing.periodicity == self.mailing.WEEK:
            return 7
        elif self.mailing.periodicity == self.mailing.MONTH:
            return calendar.monthrange(
                self.current_datetime.year, self.current_datetime.month
            )[1]
        else:
            return 0

    def __is_finished(self):
        """
        Если УКАЗАН срок окончания (а это, как правило ПЕРИОДИЧЕСКИЕ рассылки),
        и если срок окончания позади, останавливаем рассылку и возвращаем True
        """

        if self.mailing.end_datetime:
            if self.mailing.end_datetime < self.current_datetime:
                self.mailing.status = self.mailing.STOPPED
                self.mailing.save(update_fields=["status"])
                return True

        return False

    def __has_period_passed(self):
        """
        Проверяет, прошел ли период после последней отправки.
        Если прошел и это крайний срок, останавливаем рассылку
        """

        if (
            self.mailing.end_datetime
            and self.mailing.end_datetime
            < self.current_datetime + timedelta(days=self.period)
        ):
            self.mailing.status = self.mailing.STOPPED
            self.mailing.save(update_fields=["status"])

        if self.current_datetime > self.attempt.started + timedelta(days=self.period):
            return True
        return False

    def is_to_send(self):
        """
        Проверка рассылки, можно ли ее отправить?
        """

        # Если срок периодической рассылки окончен, возвращаем False
        # Эта рассылка уже не будет дальше обрабатываться
        if self.__is_finished():
            return False

        # Если последняя попытка существует И она была удачной
        self.attempt = (
            Attempt.objects.filter(mailing=self.mailing).order_by("-started").first()
        )
        if self.attempt and self.attempt.status:
            # Запускаем проверку на то, прошел ли период после последней отправки
            return self.__has_period_passed()
        else:
            # Если это разовая рассылка и она наступила,
            # останавливаем ее и возвращаем True (к отправке)
            if (
                self.period == 0
                and self.current_datetime >= self.mailing.start_datetime
            ):
                self.mailing.status = self.mailing.STOPPED
                self.mailing.end_datetime = self.current_datetime
                self.mailing.save(update_fields=["status", "end_datetime"])

        return True

    def to_runing(self):
        """
        Перевод всех рассылок в статус Запущено,
        которые находятся в промежутке времени и не являются одноразовыми
        """

        if self.mailing.periodicity != self.mailing.ONE_TIME:
            end_time = self.mailing.end_datetime
            if not end_time:
                end_time = self.current_datetime + timedelta(days=500)
            if self.mailing.start_datetime <= self.current_datetime <= end_time:
                self.mailing.status = self.mailing.RUNING
                self.mailing.save(update_fields=["status"])

    def execute(self):
        # Формирование письма


        html_content = self.mailing.text.body
        text_content = strip_tags(self.mailing.text.body)
        email = EmailMultiAlternatives(
            subject=self.mailing.text.title,
            body=text_content,
            to=[client.email for client in self.mailing.clients.all()]
        )
        email.attach_alternative(html_content, "text/html")


        # Отправка
        response_code, response_msg, status = None, None, None
        try:
            response_code = email.send(fail_silently=False)
            response_msg = "Отправлено"
            status = True
        except smtplib.SMTPException as e:
            response_code = e.smtp_code
            response_msg = e.smtp_error
            status = False
        finally:
            Attempt.objects.create(
                mailing=self.mailing,
                response_code=response_code,
                response_msg=response_msg,
                status=status,
            )


def send_mails():
    zone = pytz.timezone(settings.TIME_ZONE)
    current_datetime = datetime.now(zone)

    mailings = Mailing.objects.filter(start_datetime__lte=current_datetime).filter(
        status__in=[Mailing.CREATED, Mailing.RUNING]
    )

    for mailing in mailings:
        send_mailing = SendMailing(mailing, current_datetime)
        send_mailing.to_runing()

        if send_mailing.is_to_send():
            send_mailing.execute()
