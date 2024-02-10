from django.contrib import admin
from .models import Post


@admin.register(Post)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'slug', 'description', 'created_at', 'is_published', 'views_count')
    search_fields = ('title', 'description', 'slug')
