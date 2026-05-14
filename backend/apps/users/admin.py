from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, UserFeedback

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Fields', {'fields': ('diocese', 'notification_enabled')}),
    )

@admin.register(UserFeedback)
class UserFeedbackAdmin(admin.ModelAdmin):
    list_display = ('user', 'response_type', 'content_ref_id', 'helpful', 'created_at')
    list_filter = ('response_type', 'helpful')
    search_fields = ('user__username', 'comment')
