from django.urls import path

from sender import views
from sender.apps import SenderConfig

app_name = SenderConfig.name

urlpatterns = [
    path("", views.index, name="index"),
    path("clients/", views.ClientListView.as_view(), name="client_list"),
    path("clients/<int:pk>/", views.ClientDetailView.as_view(), name="client_detail"),
    path("clients/create/", views.ClientCreateView.as_view(), name="client_create"),
    path("clients/update/<int:pk>/", views.ClientUpdateView.as_view(), name="client_update"),
    path("clients/delete/<int:pk>/", views.ClientDeleteView.as_view(), name="client_delete"),
]
