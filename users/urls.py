from django.urls import path

from django.contrib.auth.views import LogoutView

from users import views
from users.apps import UsersConfig

app_name = UsersConfig.name

urlpatterns = [
    path("login/", views.CustomLoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
]
