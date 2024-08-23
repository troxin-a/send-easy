from datetime import datetime

from django.contrib.auth.mixins import PermissionRequiredMixin
from django.urls import reverse, reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from blog.forms import ArticleModelForm
from blog.models import Article
from blog.utils import generate_slug


class ArticleListView(PermissionRequiredMixin, ListView):
    """Список статей"""

    model = Article
    paginate_by = 5
    extra_context = {"title": "Блог"}
    permission_required = "blog.change_article"


class ArticleDetailView(DetailView):
    """Просмотр статьи"""

    model = Article

    def get_object(self, queryset=None):
        obj = super().get_object()
        obj.views_count += 1
        obj.save(update_fields=["views_count"])

        return obj


class ArticleCreateView(PermissionRequiredMixin, CreateView):
    """Создание статьи"""

    model = Article
    form_class = ArticleModelForm
    success_url = reverse_lazy("blog:list")
    extra_context = {"title": "Добавление статьи"}
    permission_required = "blog.add_article"

    def form_valid(self, form):
        if form.is_valid():
            new_article = form.save()

            # Генерация слага
            new_article.slug = generate_slug(Article, new_article.title)

            # Назначение владельца
            new_article.owner = self.request.user

            # Заполнение даты публикации при нажатии соответствующего флага
            if new_article.is_published:
                new_article.public_date = datetime.now()
            else:
                new_article.public_date = None

            new_article.save()

        return super().form_valid(form)


class ArticleUpdateView(PermissionRequiredMixin, UpdateView):
    """Редактирование статьи"""

    model = Article
    form_class = ArticleModelForm
    permission_required = "blog.change_article"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Изменение статьи"
        return context

    def form_valid(self, form):
        if form.is_valid():
            old_article = form.save()

            if old_article.is_published:
                old_article.public_date = datetime.now()
            else:
                old_article.public_date = None

            old_article.save()

        return super().form_valid(form)

    def get_success_url(self):
        return reverse("blog:detail", args=[self.kwargs.get("pk")])


class ArticleDeleteView(PermissionRequiredMixin, DeleteView):
    """Удаление статьи"""

    model = Article
    success_url = reverse_lazy("blog:list")
    permission_required = "blog.delete_article"
