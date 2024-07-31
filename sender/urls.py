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

    path("texts/", views.TextListView.as_view(), name="text_list"),
    path("texts/<int:pk>/", views.TextDetailView.as_view(), name="text_detail"),
    path("texts/create/", views.TextCreateView.as_view(), name="text_create"),
    path("texts/update/<int:pk>/", views.TextUpdateView.as_view(), name="text_update"),
    path("texts/delete/<int:pk>/", views.TextDeleteView.as_view(), name="text_delete"),
]
