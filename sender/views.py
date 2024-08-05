from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from sender.models import Attempt, Client, Text, Mailing


def index(request):
    return render(request, "sender/index.html")


class ClientListView(ListView):
    model = Client
    paginate_by = 50


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


class TextListView(ListView):
    model = Text
    paginate_by = 50


class TextDetailView(DetailView):
    model = Text


class TextCreateView(CreateView):
    model = Text
    fields = "__all__"
    success_url = reverse_lazy("sender:text_list")


class TextUpdateView(UpdateView):
    model = Text
    fields = "__all__"

    def get_success_url(self):
        return reverse("sender:text_detail", args=[self.kwargs.get("pk")])


class TextDeleteView(DeleteView):
    model = Text
    success_url = reverse_lazy("sender:text_list")


class MailingListView(ListView):
    model = Mailing
    paginate_by = 50


class MailingDetailView(DetailView):
    model = Mailing

    def get_queryset(self):        
        return Mailing.objects.all().select_related("text")

    def post(self, request, *args, **kwargs):
        """Изменение рассылки при onchange"""
        mailing = Mailing.objects.get(pk=kwargs.get('pk'))
        mailing.status = self.request.POST.get('status')
        mailing.periodicity = self.request.POST.get('periodicity')
        if mailing.periodicity == Mailing.ONE_TIME:
            mailing.end_datetime = None
            attempts = Attempt.objects.filter(mailing=mailing)
            for attempt in attempts:
                attempt.delete()
        mailing.save(update_fields=["status", "periodicity", "end_datetime"])

        return redirect("sender:mailing_detail", kwargs.get('pk'))


class MailingCreateView(CreateView):
    model = Mailing
    fields = "__all__"
    success_url = reverse_lazy("sender:mailing_list")

    def form_valid(self, form):
        if form.is_valid():
            new_mailing = form.save()
            if new_mailing.periodicity == Mailing.ONE_TIME:
                new_mailing.end_datetime = None
            new_mailing.save()
            
        return super().form_valid(form)


class MailingUpdateView(UpdateView):
    model = Mailing
    fields = "__all__"

    def form_valid(self, form):
        if form.is_valid():
            new_mailing = form.save()
            if new_mailing.periodicity == Mailing.ONE_TIME:
                new_mailing.end_datetime = None
                attempts = Attempt.objects.filter(mailing=new_mailing)
                for attempt in attempts:
                    attempt.delete()
            new_mailing.save()
            
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("sender:mailing_detail", args=[self.kwargs.get("pk")])


class MailingDeleteView(DeleteView):
    model = Mailing
    success_url = reverse_lazy("sender:mailing_list")


class AttemptDeleteView(View):

    def post(self, request, *args, **kwargs):
        attempts = Attempt.objects.filter(mailing=kwargs.get('pk'))
        for attempt in attempts:
            attempt.delete()
        return redirect("sender:mailing_detail", kwargs.get('pk'))

    
