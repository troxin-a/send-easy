from django import forms
from django_ckeditor_5.widgets import CKEditor5Widget
from sender.models import Client, Mailing, Text


class FormStyleMixin:
    """Стили для форм"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            # Скрываем поле owner
            if field_name == "owner":
                field.widget = forms.HiddenInput()
                # field.required = False
                continue
            if isinstance(field, forms.fields.BooleanField):
                field.widget.attrs.update({"class": "form-check"})
                continue
            field.widget.attrs.update({"class": "form-control"})


class ClientModelForm(FormStyleMixin, forms.ModelForm):
    """Форма клиента"""

    class Meta:
        model = Client
        fields = "__all__"


class TextModelForm(FormStyleMixin, forms.ModelForm):
    """Форма сообщения"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["body"].widget = CKEditor5Widget()

    class Meta:
        model = Text
        fields = "__all__"


class CustomDateTimeInput(forms.DateTimeInput):
    input_type = "datetime-local"


class MailingModelForm(FormStyleMixin, forms.ModelForm):
    """Форма рассылки"""

    start_datetime = forms.DateTimeField(
        widget=CustomDateTimeInput(format="%Y-%m-%dT%H:%M"),
        label="Время и дата старта",
    )
    end_datetime = forms.DateTimeField(
        widget=CustomDateTimeInput(format="%Y-%m-%dT%H:%M"),
        label="Время и дата окончания",
        required=False,
    )

    class Meta:
        model = Mailing
        fields = "__all__"
