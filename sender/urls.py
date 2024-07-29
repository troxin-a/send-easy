from django.urls import path

from sender import views
from sender.apps import SenderConfig

app_name = SenderConfig.name

urlpatterns = [
    path("", views.index, name="index"),
]
