from django.contrib import admin
from ads.models import Ad


@admin.register(Ad)
class AdAdmin(admin.ModelAdmin):
    list_display = ('title', 'duration', 'priority', 'is_active', 'start_date', 'end_date', 'created_at')
    search_fields = ('title',)
    list_filter = ('is_active', 'priority')
