from django.contrib import admin
from .models import Emotion, DevotionalContent, UserDevotional

@admin.register(Emotion)
class EmotionAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'icon')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(DevotionalContent)
class DevotionalContentAdmin(admin.ModelAdmin):
    list_display = ('title', 'emotion', 'is_active', 'ai_generated', 'created_at')
    list_filter = ('emotion', 'is_active', 'ai_generated')
    search_fields = ('title', 'scripture_reference')

@admin.register(UserDevotional)
class UserDevotionalAdmin(admin.ModelAdmin):
    list_display = ('user', 'content', 'accessed_at')
    list_filter = ('accessed_at',)
    search_fields = ('user__username', 'content__title')
