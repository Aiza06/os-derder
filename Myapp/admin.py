from django.contrib import admin
from .models import Story


@admin.register(Story)
class StoryAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "author_name",
        "genre",
        "chapter",
        "status",
        "rating",
        "date_published",
    )

    list_filter = (
        "status",
        "genre",
    )

    search_fields = (
        "title",
        "author_name",
        "genre",
    )

    ordering = (
        "-date_published",
    )