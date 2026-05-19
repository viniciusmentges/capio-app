from django.db import models
from django.conf import settings

class Emotion(models.Model):
    name = models.CharField(max_length=80)
    slug = models.SlugField(unique=True)
    icon = models.CharField(max_length=80, blank=True)

    def __str__(self):
        return self.name

class DevotionalContent(models.Model):
    emotion = models.ForeignKey(Emotion, on_delete=models.CASCADE, related_name='devotionals')
    passage = models.ForeignKey('bible.BiblePassage', on_delete=models.SET_NULL, null=True, blank=True, related_name='devotionals')
    title = models.CharField(max_length=180)
    scripture_reference = models.CharField(max_length=150)
    scripture_text = models.TextField()
    reflection = models.TextField()
    practical_application = models.TextField(blank=True)
    guiding_question = models.TextField(blank=True)
    prayer = models.TextField()
    share_quote = models.TextField(blank=True, default='')
    emotional_theme = models.CharField(max_length=150, blank=True, default='')
    reviewed_by_human = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    ai_generated = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def resolve_passage(self):
        if self.scripture_reference and self.scripture_reference.strip():
            from services.bible.normalization import NormalizationService
            from apps.bible.models import BiblePassage
            
            can_id, book, chap, verses = NormalizationService.normalize(self.scripture_reference)
            
            # Garantir canonical_id consistente
            passage = BiblePassage.objects.filter(canonical_id=can_id).first()
            if not passage:
                passage = BiblePassage.objects.create(
                    canonical_id=can_id,
                    book_name=book,
                    chapter=chap,
                    verses=verses or "",
                    text_original=self.scripture_text or "A Palavra de Deus...",
                    translation="NVI",
                    language="pt"
                )
            elif self.scripture_text and (not passage.text_original or passage.text_original.startswith("A Palavra de Deus")):
                passage.text_original = self.scripture_text
                passage.save(update_fields=['text_original'])
                
            self.passage = passage

    def clean(self):
        from django.core.exceptions import ValidationError
        errors = {}
        if not self.emotion_id:
            errors['emotion'] = "A emoção é obrigatória."
        if not self.scripture_reference or not self.scripture_reference.strip():
            errors['scripture_reference'] = "A referência bíblica é obrigatória."
        if not self.scripture_text or not self.scripture_text.strip():
            errors['scripture_text'] = "O texto bíblico é obrigatório."
        if not self.reflection or not self.reflection.strip():
            errors['reflection'] = "A reflexão contemplativa é obrigatória."
        if not self.prayer or not self.prayer.strip():
            errors['prayer'] = "A oração é obrigatória."
        if not self.share_quote or not self.share_quote.strip():
            errors['share_quote'] = "O fragmento compartilhável (share_quote) é obrigatório."
            
        try:
            self.resolve_passage()
        except Exception as e:
            errors['scripture_reference'] = f"Erro ao processar referência bíblica: {str(e)}"
            
        if (self.is_active or self.reviewed_by_human) and not self.passage:
            errors['passage'] = "O relacionamento 'passage' (BiblePassage) é obrigatório para devocionais ativos ou revisados por humanos."
            
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.resolve_passage()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} ({self.emotion.name})"

class UserDevotional(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='devotional_history')
    content = models.ForeignKey(DevotionalContent, on_delete=models.CASCADE, related_name='accessed_by')
    accessed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.content.title}"
