from django.contrib import admin
from .models import Emotion, DevotionalContent, UserDevotional

@admin.register(Emotion)
class EmotionAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'icon')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(DevotionalContent)
class DevotionalContentAdmin(admin.ModelAdmin):
    list_display = ('title', 'emotion', 'emotional_theme', 'reviewed_by_human', 'is_active', 'ai_generated', 'created_at')
    list_filter = ('emotion', 'reviewed_by_human', 'is_active', 'ai_generated')
    search_fields = ('title', 'scripture_reference', 'reflection', 'share_quote')
    ordering = ('-created_at',)
    
    # Campos apenas de leitura
    readonly_fields = ('created_at',)
    
    # Ações em lote no admin
    actions = ['generate_share_quotes_action']

    @admin.action(description="✨ Gerar Share Quotes ausentes em lote com IA")
    def generate_share_quotes_action(self, request, queryset):
        from services.ai import get_ai_service
        import time
        from django.contrib import messages

        ai_service = get_ai_service()
        updated_count = 0
        skipped_count = 0

        for dev in queryset:
            # Pular se já tem uma frase compartilhável válida
            if dev.share_quote and dev.share_quote.strip() not in ["", "None", "nan", "NoneType"]:
                skipped_count += 1
                continue

            if not dev.reflection:
                skipped_count += 1
                continue

            try:
                quote = ai_service.generate_share_quote(dev.reflection)
                quote = quote.strip().strip('"').strip("'").strip('“').strip('”')
                if quote:
                    dev.share_quote = quote
                    dev.save(update_fields=['share_quote'])
                    updated_count += 1
                    time.sleep(0.5)
            except Exception as e:
                self.message_user(request, f"Erro ao gerar para ID {dev.id}: {str(e)}", messages.ERROR)

        self.message_user(
            request, 
            f"✨ Geração em lote finalizada! {updated_count} devocionais atualizados. {skipped_count} ignorados por já possuírem frase ou estarem sem meditação.",
            messages.SUCCESS
        )

    # Organização visual em grupos (Fieldsets)
    fieldsets = (
        ('Identificação e Metadados', {
            'fields': ('emotion', 'emotional_theme', 'title', 'created_at'),
            'description': 'Configure a classificação emocional e metadados fundamentais.'
        }),
        ('Fundação Bíblica (Scripture-First)', {
            'fields': ('passage', 'scripture_reference', 'scripture_text'),
            'description': 'O alicerce bíblico contendo a referência normalizada, passagem e texto sagrado.'
        }),
        ('Roteiro Contemplativo', {
            'fields': ('reflection', 'share_quote'),
            'description': 'A reflexão meditativa profunda e a sentença contemplativa compartilhável da CAPIO.'
        }),
        ('Aplicação Prática e Recolhimento', {
            'fields': ('practical_application', 'guiding_question', 'prayer'),
            'description': 'Eco na vida diária, a pergunta orientadora íntima e a oração de repouso final.'
        }),
        ('Status de Curadoria e Publicação', {
            'fields': ('ai_generated', 'reviewed_by_human', 'is_active'),
            'description': 'Marque "Revisado por Humano" e "Ativo" para validar e liberar a leitura na biblioteca pública.'
        }),
    )

    # Injeção de Media para o botão de geração inteligente
    class Media:
        js = ('admin/js/editorial_ia.js',)
        css = {
            'all': ('admin/css/editorial_ia.css',)
        }

@admin.register(UserDevotional)
class UserDevotionalAdmin(admin.ModelAdmin):
    list_display = ('user', 'content', 'accessed_at')
    list_filter = ('accessed_at',)
    search_fields = ('user__username', 'content__title')
