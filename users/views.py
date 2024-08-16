from django.shortcuts import render
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView

from users.forms import CustomAuthenticationForm


class CustomLoginView(LoginView):
    form_class = CustomAuthenticationForm
    template_name = "users/login.html"
