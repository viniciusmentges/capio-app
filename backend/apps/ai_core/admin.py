from django.contrib import admin
from .models import AIRequest, GeneratedResponse

@admin.register(AIRequest)
class AIRequestAdmin(admin.ModelAdmin):
    list_display = ('request_type', 'status', 'flagged_for_review', 'duration_ms', 'created_at')
    list_filter = ('request_type', 'status', 'flagged_for_review')
    search_fields = ('input_hash',)

@admin.register(GeneratedResponse)
class GeneratedResponseAdmin(admin.ModelAdmin):
    list_display = ('response_type', 'filter_status', 'user', 'content_ref_id', 'created_at')
    list_filter = ('response_type', 'filter_status', 'created_at')
    search_fields = ('user__username', 'content_ref_id')
