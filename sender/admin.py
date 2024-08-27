from django.contrib import admin

from sender.models import Attempt, Client, Mailing, Text


class MembershipInline(admin.TabularInline):
    model = Mailing.clients.through
    verbose_name = "рассылку"
    verbose_name_plural = "рассылки"
    extra = 0


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    fields = (
        "owner",
        "name",
        "email",
        "comment",
    )
    list_display = (
        "name",
        "email",
        "get_comment",
    )
    search_fields = (
        "name",
        "email",
        "comment",
    )
    inlines = [
        MembershipInline,
    ]

    def get_comment(self, obj):
        if len(obj.comment) >= 100:
            return obj.comment[:100] + "..."
        return obj.comment


@admin.register(Text)
class TextAdmin(admin.ModelAdmin):

    list_display = ("title",)
    search_fields = (
        "title",
        "body",
    )


@admin.register(Mailing)
class MailingAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "start_datetime",
        "end_datetime",
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


@admin.register(Attempt)
class AttemptAdmin(admin.ModelAdmin):
    list_display = (
        "mailing",
        "started",
        "status",
        "response_code",
        "response_msg",
    )
    search_fields = (
        "mailing.name",
        "response_msg",
    )
    list_filter = (
        "mailing",
        "status",
        "response_code",
    )
