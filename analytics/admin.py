from django.contrib import admin
from analytics.models import PlayLog


@admin.register(PlayLog)
class PlayLogAdmin(admin.ModelAdmin):
    list_display = ('device', 'ad', 'played_at')
    list_filter = ('device', 'ad')
