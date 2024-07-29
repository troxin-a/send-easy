from django.contrib import admin

from sender.models import Client, Mailing, Text


class MembershipInline(admin.TabularInline):
    model = Mailing.clients.through
    verbose_name = "рассылку"
    verbose_name_plural = "рассылки"
    extra = 0



@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    fields = (
        "name",
        "email",
        "comment",
    )
    list_display = (
        "name",
        "email",
        "comment",
    )
    search_fields = (
        "name",
        "email",
        "comment",
    )
    inlines = [
        MembershipInline,
    ]


@admin.register(Text)
class TextAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "body",
    )
    search_fields = (
        "title",
        "body",
    )


@admin.register(Mailing)
class MailingAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "started_at",
        "periodicity",
        "status",
        "text",
    )
    list_editable = (
        "periodicity",
        "status",
    )
    filter_horizontal = ("clients",)

    search_fields = (
        "title",
        "body",
    )
    list_filter = (
        "periodicity",
        "status",
    )
