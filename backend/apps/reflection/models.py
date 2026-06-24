import uuid
from django.db import models
from django.conf import settings

class DailyReflection(models.Model):
    public_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    date = models.DateField(unique=True)
    passage = models.ForeignKey('bible.BiblePassage', on_delete=models.SET_NULL, null=True, blank=True, related_name='daily_reflections')
    title = models.CharField(max_length=180)
    scripture_reference = models.CharField(max_length=150)
    scripture_text = models.TextField()
    reflection_body = models.TextField()
    guiding_question = models.TextField()
    closing_prayer = models.TextField()
    
    # --- ATIVO EDITORIAL: share_quote ---
    # Este campo representa a assinatura editorial compartilhável do dia.
    share_quote = models.TextField(blank=True, default="")
    
    # --- ATIVOS NOTURNOS ---
    night_word = models.TextField(blank=True, default="")
    night_prayer = models.TextField(blank=True, default="")
    
    ai_generated = models.BooleanField(default=False)
    
    # Eixos editoriais da Fase 2 para Thematic Steering
    emotional_theme = models.CharField(max_length=100, blank=True, default="")
    theme_key = models.CharField(max_length=50, blank=True, default="")

    def __str__(self):
        return f"{self.date} - {self.title}"

class UserReflectionResponse(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reflection_responses')
    reflection = models.ForeignKey(DailyReflection, on_delete=models.CASCADE, related_name='responses')
    response_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'reflection')

    def __str__(self):
        return f"Response by {self.user.username} for {self.reflection.date}"

class EditorialFragment(models.Model):
    FRAGMENT_TYPES = [
        ('quote', 'Assinatura Poética'),
        ('prayer', 'Oração Breve'),
        ('scripture', 'Fragmento Bíblico'),
        ('question', 'Pergunta Guia')
    ]
    reflection = models.ForeignKey(
        DailyReflection, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='fragments'
    )
    devotional = models.ForeignKey(
        'devotional.DevotionalContent', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='fragments'
    )
    content_text = models.TextField()
    fragment_type = models.CharField(max_length=20, choices=FRAGMENT_TYPES, default='quote')
    theme_key = models.CharField(max_length=50, blank=True, default="")
    share_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_fragment_type_display()} - {self.content_text[:30]}..."

class ContemplativeExperience(models.Model):
    EXPERIENCE_TYPES = [
        ('audio_reflection', 'Meditação em Áudio'),
        ('guided_prayer', 'Oração Guada'),
        ('spiritual_path', 'Trilha de Silêncio')
    ]
    title = models.CharField(max_length=200)
    description = models.TextField()
    experience_type = models.CharField(max_length=30, choices=EXPERIENCE_TYPES)
    audio_url = models.CharField(max_length=255, blank=True, default="")
    duration_seconds = models.IntegerField(default=0)
    is_premium = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.get_experience_type_display()}] {self.title}"

class SpiritualCollection(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    theme_key = models.CharField(max_length=50, blank=True, default="")
    is_premium = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

