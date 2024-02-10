from django.contrib import admin
from .models import Client


@admin.register(Client)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'name', 'surname', 'patronymic', 'owner')
    list_filter = ('surname', 'name',)
    search_fields = ('email', 'name', 'surname',)
