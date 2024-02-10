from django.contrib import admin

from distribution.models import MailingSettings, Message, MailingLog


@admin.register(Message)
class MessageListSettingsAdmin(admin.ModelAdmin):
    list_display = ('pk', 'title', 'owner',)
    list_filter = ('title',)
    search_fields = ('title', 'text',)


@admin.register(MailingSettings)
class MailingListSettingsAdmin(admin.ModelAdmin):
    list_display = ('pk', 'start_time', 'end_time', 'next_send', 'periodicity', 'status', 'is_active', 'owner',)
    list_filter = ('next_send', 'periodicity', 'status', 'owner',)
    search_fields = ('start_time', 'periodicity', 'end_time', 'owner',)


@admin.register(MailingLog)
class LogAdmin(admin.ModelAdmin):
    list_display = ('pk', 'mailing', 'time', 'status', 'server_response', 'owner',)
    list_filter = ('time', 'status', 'owner',)
    search_fields = ('mailing', 'time', 'status', 'owner',)
