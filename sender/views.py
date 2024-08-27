from django.contrib.auth.decorators import permission_required
from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    UserPassesTestMixin,
)
from django.core.exceptions import PermissionDenied
from django.forms import ValidationError
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

from blog.models import Article
from sender.forms import ClientModelForm, MailingModelForm, TextModelForm
from sender.models import Attempt, Client, Text, Mailing
from sender.services import get_statistic_from_cache


def index(request):
    """Главная страница"""

    statistic = get_statistic_from_cache()
    articles = Article.objects.order_by("?")[:3]

    context = {
        "mailings_count": statistic.get("mailings_count"),
        "mailings_count_active": statistic.get("mailings_active_count"),
        "clients_count": statistic.get("clients_count"),
        "articles": articles,
    }

    return render(request, "sender/index.html", context)


class ViewAccessMixin:
    """
    Показывает всё тем, у кого есть соответствующее разрешение,
    и скрывает от рядового пользователя чужое
    """

    def get_queryset(self):
        if self.request.user.has_perm(getattr(self, "permission_required", None)):
            return self.model.objects.all()
        return self.model.objects.filter(owner=self.request.user)


class ActionUserPassesTestMixin(UserPassesTestMixin):
    """Разрешает действия только владельцу или суперпользователю"""

    def test_func(self):
        user = self.request.user
        obj = self.get_object()
        return obj.owner == user or user.is_superuser


class ModeratorPassesTestMixin(UserPassesTestMixin):
    """Запрещает просмотр модераторам"""

    def test_func(self):
        return not self.request.user.is_staff


class CreatePermissionMixin:
    """Разрешает создавать объект всем, кроме модератора"""

    def get_form_class(self):
        if self.request.user.has_perms(
            [
                "users.block_user",
                "sender.disable_mailing",
            ]
        ):
            raise PermissionDenied
        return self.form_class


class ClientListView(
    LoginRequiredMixin, ViewAccessMixin, ModeratorPassesTestMixin, ListView
):
    """
    Список клиентов
    permission_required не назначен: список видят только владельцы
    Доступ к списку модератору запрещен
    """

    model = Client
    paginate_by = 50


class ClientDetailView(LoginRequiredMixin, ViewAccessMixin, DetailView):
    """Просмотр клиента"""

    model = Client
    permission_required = "sender.view_client"


class ClientCreateView(LoginRequiredMixin, CreatePermissionMixin, CreateView):
    """Добавление клиента"""

    model = Client
    form_class = ClientModelForm
    success_url = reverse_lazy("sender:client_list")

    def form_valid(self, form):
        user = self.request.user
        if form.is_valid:
            obj = form.save(commit=False)
            if Client.objects.filter(owner=user).filter(email=obj.email).exists():
                form.add_error("email", ValidationError("Клиент с такой почтой у Вас уже есть"))
                return self.form_invalid(form)
            obj.owner = user
            obj.save()

        return super().form_valid(form)


class ClientUpdateView(LoginRequiredMixin, ActionUserPassesTestMixin, UpdateView):
    """Редактирование клиента"""

    model = Client
    form_class = ClientModelForm

    def get_success_url(self):
        return reverse("sender:client_detail", args=[self.kwargs.get("pk")])


class ClientDeleteView(LoginRequiredMixin, ActionUserPassesTestMixin, DeleteView):
    """Удаление клиента"""

    model = Client
    success_url = reverse_lazy("sender:client_list")


class TextListView(
    LoginRequiredMixin, ViewAccessMixin, ModeratorPassesTestMixin, ListView
):
    """
    Список сообщений
    permission_required не назначен: список видят только владельцы
    Доступ к списку модератору запрещен
    """

    model = Text
    paginate_by = 50


class TextDetailView(LoginRequiredMixin, ViewAccessMixin, DetailView):
    """Просмотр сообщения"""

    model = Text
    permission_required = "sender.view_text"


class TextCreateView(LoginRequiredMixin, CreatePermissionMixin, CreateView):
    """Создание сообщения"""

    model = Text
    form_class = TextModelForm
    success_url = reverse_lazy("sender:text_list")

    def form_valid(self, form):
        if form.is_valid:
            obj = form.save()
            obj.owner = self.request.user

        return super().form_valid(form)


class TextUpdateView(LoginRequiredMixin, ActionUserPassesTestMixin, UpdateView):
    """Редактирование сообщения"""

    model = Text
    form_class = TextModelForm

    def get_success_url(self):
        return reverse("sender:text_detail", args=[self.kwargs.get("pk")])


class TextDeleteView(LoginRequiredMixin, ActionUserPassesTestMixin, DeleteView):
    """Удаление сообщения"""

    model = Text
    success_url = reverse_lazy("sender:text_list")


class MailingListView(LoginRequiredMixin, ViewAccessMixin, ListView):
    """Список рассылок"""

    model = Mailing
    paginate_by = 50
    permission_required = "sender.view_mailing"


class MailingDetailView(LoginRequiredMixin, ViewAccessMixin, DetailView):
    """Просмотр рассылки"""

    model = Mailing
    permission_required = "sender.view_mailing"

    def get_queryset(self):
        return super().get_queryset().select_related("text").prefetch_related("clients")

    def post(self, request, *args, **kwargs):
        """Изменение рассылки при onchange"""
        mailing = Mailing.objects.get(pk=kwargs.get("pk"))
        mailing.status = self.request.POST.get("status")
        mailing.periodicity = self.request.POST.get("periodicity")
        if mailing.periodicity == Mailing.ONE_TIME:
            mailing.end_datetime = None
            attempts = Attempt.objects.filter(mailing=mailing)
            for attempt in attempts:
                attempt.delete()
        mailing.save(update_fields=["status", "periodicity", "end_datetime"])

        return redirect("sender:mailing_detail", kwargs.get("pk"))


class MailingValidMixin:
    def form_valid(self, form):
        if form.is_valid():
            new_mailing = form.save(commit=False)
            # Если это не одноразовая рассылка, сверяем даты.
            if new_mailing.periodicity != Mailing.ONE_TIME:
                if new_mailing.start_datetime > new_mailing.end_datetime:
                    form.add_error(
                        "start_datetime",
                        "Дата старта не может быть позже даты окончания",
                    )
                    return self.form_invalid(form)
            else:
                # Если это одноразовая рассылка,
                # чистим дату окончания и все попытки, если были
                new_mailing.end_datetime = None
                attempts = Attempt.objects.filter(mailing=new_mailing)
                if attempts:
                    for attempt in attempts:
                        attempt.delete()
            new_mailing.save()

        return super().form_valid(form)


class MailingCreateView(
    LoginRequiredMixin, CreatePermissionMixin, MailingValidMixin, CreateView
):
    """Создание рассылки"""

    model = Mailing
    form_class = MailingModelForm
    success_url = reverse_lazy("sender:mailing_list")


class MailingUpdateView(
    LoginRequiredMixin, ActionUserPassesTestMixin, MailingValidMixin, UpdateView
):
    """Редактирование рассылки"""

    model = Mailing
    form_class = MailingModelForm

    def get_success_url(self):
        return reverse("sender:mailing_detail", args=[self.kwargs.get("pk")])


class MailingDeleteView(LoginRequiredMixin, ActionUserPassesTestMixin, DeleteView):
    """Удаление рассылки"""

    model = Mailing
    success_url = reverse_lazy("sender:mailing_list")


@permission_required("sender.disable_mailing", PermissionDenied)
def disable_mailing(request, pk):
    """Отключение рассылки может осуществлять только модератор"""

    mailing = Mailing.objects.get(pk=pk)
    if mailing.status != mailing.STOPPED:
        mailing.status = mailing.STOPPED
        mailing.save(update_fields=["status"])

    return redirect(reverse("sender:mailing_detail", args=[mailing.pk]))


class AttemptDeleteView(LoginRequiredMixin, ActionUserPassesTestMixin, View):
    """Удаление логов конкретной рассылки"""

    def post(self, request, *args, **kwargs):
        attempts = Attempt.objects.filter(mailing=kwargs.get("pk"))
        for attempt in attempts:
            attempt.delete()
        return redirect("sender:mailing_detail", kwargs.get("pk"))
