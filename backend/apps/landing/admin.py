from django.contrib import admin
from .models import LandingScreenshot
from django.utils.html import format_html

@admin.register(LandingScreenshot)
class LandingScreenshotAdmin(admin.ModelAdmin):
    list_display = ('title', 'key', 'is_active', 'sort_order', 'image_preview', 'updated_at')
    list_filter = ('is_active', 'key')
    search_fields = ('title', 'key', 'alt_text')
    ordering = ('sort_order', 'id')
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="height: 50px; border-radius: 4px;"/>', obj.image.url)
        return "-"
    image_preview.short_description = "Preview"
