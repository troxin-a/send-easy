from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from sender.models import Client


def index(request):
    return render(request, "sender/index.html")


class ClientListView(ListView):
    model = Client
    paginate_by = 100


class ClientDetailView(DetailView):
    model = Client


class ClientCreateView(CreateView):
    model = Client
    fields = "__all__"
    success_url = reverse_lazy("sender:client_list")


class ClientUpdateView(UpdateView):
    model = Client
    fields = "__all__"

    def get_success_url(self):
        return reverse("sender:client_detail", args=[self.kwargs.get("pk")])


class ClientDeleteView(DeleteView):
    model = Client
    success_url = reverse_lazy("sender:client_list")
