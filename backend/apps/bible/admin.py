from django.contrib import admin
from .models import PassageExplanation

@admin.register(PassageExplanation)
class PassageExplanationAdmin(admin.ModelAdmin):
    list_display = ('reference_display', 'reference_normalized', 'ai_generated', 'created_at')
    list_filter = ('ai_generated',)
    search_fields = ('reference_normalized', 'reference_display')
