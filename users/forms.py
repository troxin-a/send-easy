from django.contrib.auth.forms import (
    AuthenticationForm,
    UserChangeForm,
    UserCreationForm,
    PasswordChangeForm,
    PasswordResetForm,
    SetPasswordForm,
)
from django import forms


from users.models import User


class FormStyleMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs.update({"class": "form-control"})


class CustomUserCreationForm(FormStyleMixin, UserCreationForm):
    """Форма регистрации"""

    class Meta:
        model = User
        fields = (
            "email",
            "password1",
            "password2",
        )


class CustomAuthenticationForm(FormStyleMixin, AuthenticationForm):
    """Форма авторизации"""


class CustomUserChangeForm(FormStyleMixin, UserChangeForm):
    """Форма профиля пользователя"""

    password = forms.CharField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = User
        fields = (
            "email",
            "first_name",
            "last_name",
        )


class CustomPasswordChangeForm(FormStyleMixin, PasswordChangeForm):
    """Форма смены пароля"""


class CustomPasswordResetForm(FormStyleMixin, PasswordResetForm):
    """Форма сброса пароля"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["email"].widget.attrs.update(
            {"placeholder": "Укажите email, указанный при регистрации"}
        )


class CustomSetPasswordForm(FormStyleMixin, SetPasswordForm):
    """Форма установки пароля после сброса"""
