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

    path("mailings/", views.MailingListView.as_view(), name="mailing_list"),
    path("mailings/<int:pk>/", views.MailingDetailView.as_view(), name="mailing_detail"),
    path("mailings/create/", views.MailingCreateView.as_view(), name="mailing_create"),
    path("mailings/update/<int:pk>/", views.MailingUpdateView.as_view(), name="mailing_update"),
    path("mailings/delete/<int:pk>/", views.MailingDeleteView.as_view(), name="mailing_delete"),
]
