import re
from django.contrib import admin
from .models import DailyReflection, UserReflectionResponse

@admin.register(DailyReflection)
class DailyReflectionAdmin(admin.ModelAdmin):
    list_display = (
        "date",
        "title",
        "theme_key",
        "emotional_theme",
        "scripture_reference",
        "ai_generated"
    )
    list_filter = (
        "theme_key",
        "ai_generated",
        "date"
    )
    search_fields = (
        "title",
        "reflection_body",
        "emotional_theme",
        "scripture_reference"
    )
    readonly_fields = (
        "theme_key",
        "emotional_theme"
    )
    
    def changelist_view(self, request, extra_context=None):
        from services.reflection.editorial_analytics import generate_editorial_report
        extra_context = extra_context or {}
        
        # Gera o relatório curatorial de observabilidade
        report = generate_editorial_report(days=30)
        
        # Formata o markdown em tags HTML para renderização elegante no console monástico
        # Remove títulos brutas com markdown e envolve em spans/h3
        html_report = report.replace('### ', '<h3 style="color: #f5c2e7; margin-top: 0; margin-bottom: 12px; border-bottom: 1px solid #45475a; padding-bottom: 8px; font-family: sans-serif; font-size: 15px;">')
        
        # Expressões regulares para formatar o restante do markdown
        html_report = re.sub(r'\*\*(.*?)\*\*', r'<strong style="color: #a6e3a1;">\1</strong>', html_report)
        html_report = re.sub(r'\*(.*?)\*', r'<em style="color: #89b4fa;">\1</em>', html_report)
        
        # Listas
        html_report = html_report.replace('  - ', '&nbsp;&nbsp;&bull; ')
        html_report = html_report.replace('* ', '&bull; ')
        
        # Quebras de linha
        html_report = html_report.replace('\n', '<br>')
        
        extra_context['editorial_report'] = html_report
        return super().changelist_view(request, extra_context=extra_context)

@admin.register(UserReflectionResponse)
class UserReflectionResponseAdmin(admin.ModelAdmin):
    list_display = ('user', 'reflection', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'response_text')
