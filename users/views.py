from secrets import token_hex
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import EmailMessage
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
from django.views.generic import UpdateView, CreateView

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
