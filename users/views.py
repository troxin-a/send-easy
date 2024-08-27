from secrets import token_hex
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    UserPassesTestMixin,
)
from django.core.exceptions import PermissionDenied
from django.core.mail import EmailMessage
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy, reverse
from django.contrib.auth.views import (
    LoginView,
    PasswordChangeView,
    PasswordChangeDoneView,
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView,
)
from django.views.generic import ListView, UpdateView, CreateView

from sender.models import Mailing
from users.forms import (
    CustomAuthenticationForm,
    CustomPasswordChangeForm,
    CustomPasswordResetForm,
    CustomSetPasswordForm,
    CustomUserChangeForm,
    CustomUserCreationForm,
)
from users.models import User


class UserCreateView(CreateView):
    """Регистрация"""

    model = User
    form_class = CustomUserCreationForm
    template_name = "users/auth.html"
    success_url = reverse_lazy("users:info")
    extra_context = {
        "title": "Регистрация",
        "button": "Регистрация",
    }

    def form_valid(self, form):
        """Генерация токена и отправка подтверждения email"""
        if form.is_valid:
            user = form.save()
            token = token_hex(8)
            user.is_active = False
            user.token = token

            host = self.request.get_host()
            tail = reverse("users:confirm_email", args=[token])
            email_body = f"Перейдите по ссылке, чтобы подтвердить регистрацию: http://{host}{tail}"

            email = EmailMessage(
                subject="Подтверждение регистрации",
                body=email_body,
                to=[
                    user.email,
                ],
            )
            email.send(fail_silently=False)

        return super().form_valid(form)


def confirm_email(request, token):
    user = get_object_or_404(User, token=token)
    user.is_active = True
    user.token = None
    user.save(update_fields=["is_active", "token"])
    return redirect(reverse("users:login"))


def info_confirm_email(request):
    context = {
        "title": "Подтверждение регистрации",
        "text": "На Ваш email отправлена ссылка для подтверждения регистрации",
    }
    return render(request, "users/info.html", context)


class CustomLoginView(LoginView):
    """Авторизация"""

    form_class = CustomAuthenticationForm
    template_name = "users/auth.html"
    extra_context = {
        "title": "Авторизация",
        "button": "Вход",
        "forget_pass": True,
    }


class ProfileView(LoginRequiredMixin, UpdateView):
    """Профиль пользователя"""

    form_class = CustomUserChangeForm
    template_name = "users/auth.html"
    success_url = reverse_lazy("users:profile")
    extra_context = {
        "title": "Профиль",
        "button": "Сохранить",
        "change_pass": "Сменить пароль",
    }

    def get_object(self):
        return self.request.user


class CustomPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    """Смена пароля"""

    form_class = CustomPasswordChangeForm
    success_url = reverse_lazy("users:password_change_done")
    template_name = "users/auth.html"
    extra_context = {
        "button": "Сменить пароль",
    }


class CustomPasswordChangeDoneView(LoginRequiredMixin, PasswordChangeDoneView):
    """Успешное изменение пароля"""

    template_name = "users/info.html"
    extra_context = {
        "text": "Пароль успешно установлен",
    }


class CustomPasswordResetView(PasswordResetView):
    """Сброс пароля забываки"""

    form_class = CustomPasswordResetForm
    template_name = "users/auth.html"
    email_template_name = "users/password_reset_email.html"
    success_url = reverse_lazy("users:password_reset_done")
    extra_context = {
        "button": "Отправить",
    }


class CustomPasswordResetDoneView(PasswordResetDoneView):
    """Сообщение с инструкцией сброса пароля"""

    template_name = "users/info.html"


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    """Установка пароля после сброса"""

    form_class = CustomSetPasswordForm
    template_name = "users/auth.html"
    success_url = reverse_lazy("users:password_reset_complete")
    extra_context = {
        "button": "Отправить",
    }


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    """Сообщение об успешном восстановлении пароля"""

    template_name = "users/info.html"
    extra_context = {
        "text": "Пароль успешно восстановлен, теперь можете войти",
        "link": {
            "caption": "Войти",
            "link": reverse_lazy("users:login"),
        },
    }


class UserListView(UserPassesTestMixin, ListView):
    """Список пользователей сервиса. Виден только модератору и админу"""

    paginate_by = 50

    def test_func(self):
        user = self.request.user
        return user.has_perm("users.view_user") or user.is_superuser

    def get_queryset(self):
        queryset = User.objects.all()
        if self.request.user.is_superuser:
            return queryset
        return queryset.filter(is_superuser=False)


@permission_required("users.block_user", PermissionDenied)
def change_user_activity(request, pk):
    """
    Изменение статуса пользователя.
    Во время блокировки останавливаются все его рассылки
    """

    user = User.objects.get(pk=pk)

    # Админа и персонал деактивировать нельзя (только из админки)
    if user.is_superuser or user.is_staff:
        raise PermissionDenied

    if user.is_active:
        # Блокировка
        user.is_active = False

        # Остановка всех рассылок
        update_list = []
        for mailing in user.mailings.exclude(status=Mailing.STOPPED):
            mailing.status = mailing.STOPPED
            update_list.append(mailing)
        # Сохранение всех объектов одной транзакцией
        with transaction.atomic():
            for record in update_list:
                record.save(update_fields=["status"])
    else:
        # Активация
        user.is_active = True
    user.save(update_fields=("is_active",))

    return redirect(reverse_lazy("users:user_list"))
