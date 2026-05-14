from django.contrib import admin
from .models import DailyReflection, UserReflectionResponse

@admin.register(DailyReflection)
class DailyReflectionAdmin(admin.ModelAdmin):
    list_display = ('date', 'title', 'ai_generated')
    list_filter = ('ai_generated', 'date')
    search_fields = ('title', 'scripture_reference')

@admin.register(UserReflectionResponse)
class UserReflectionResponseAdmin(admin.ModelAdmin):
    list_display = ('user', 'reflection', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'response_text')
