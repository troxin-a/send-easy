from django.contrib import admin

from blog.models import Article


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    fields = (
        "title",
        "slug",
        "content",
        "preview",
        "views_count",
        "public_date",
        "is_published",
    )
    readonly_fields = (
        "views_count",
        "public_date",
    )
    list_display = (
        "title",
        "public_date",
        "is_published",
    )
    list_filter = (
        "is_published",
    )
    search_fields = (
        "title",
        "content",
    )
    prepopulated_fields = {'slug': ('title',)}
