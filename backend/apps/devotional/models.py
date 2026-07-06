from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
import logging
import uuid

logger = logging.getLogger(__name__)

class Emotion(models.Model):
    name = models.CharField(max_length=80)
    slug = models.SlugField(unique=True)
    icon = models.CharField(max_length=80, blank=True)

    def __str__(self):
        return self.name

SHARE_BACKGROUND_CHOICES = [
    ("gradient_light", "Fundo padrão claro"),
    ("gradient_dark", "Fundo padrão escuro"),
    ("window_light", "Luz da janela"),
    ("coffee_table", "Mesa com café"),
]

class DevotionalContent(models.Model):
    public_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
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
    main_truth = models.TextField(blank=True, default='', help_text="O Fio da Palavra: a verdade central da reflexão.")
    daily_companion = models.TextField(blank=True, default='', help_text="A Palavra Continua: pensamento silencioso para o dia.")
    share_text = models.CharField(max_length=110, blank=True, default='', help_text="Frase pastoral curta para repost. Máx 110 caracteres.")
    share_bg_image = models.CharField(max_length=50, blank=True, choices=SHARE_BACKGROUND_CHOICES, default='gradient_light', help_text="Selecione o fundo da imagem de compartilhamento.")
    emotional_theme = models.CharField(max_length=150, blank=True, default='')
    reviewed_by_human = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    ai_generated = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def resolve_passage(self):
        logger.debug(
            "[CAPIO PASSAGE DEBUG] resolve_passage() start devotional_id=%s reference=%r has_text=%s",
            self.pk,
            self.scripture_reference,
            bool(self.scripture_text and self.scripture_text.strip()),
        )
        if self.scripture_reference and self.scripture_reference.strip():
            from services.bible.normalization import NormalizationService
            from apps.bible.models import BiblePassage
            
            can_id, book, chap, verses = NormalizationService.normalize(self.scripture_reference)
            if verses:
                can_id = f"{can_id}.{verses}"
            logger.debug(
                "[CAPIO PASSAGE DEBUG] NormalizationService result canonical_id=%s book=%s chapter=%s verses=%s",
                can_id,
                book,
                chap,
                verses,
            )
            
            # Garantir canonical_id consistente
            passage = BiblePassage.objects.filter(canonical_id=can_id).first()
            created = False
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
                created = True
            elif self.scripture_text and (not passage.text_original or passage.text_original.startswith("A Palavra de Deus")):
                passage.text_original = self.scripture_text
                passage.save(update_fields=['text_original'])

            logger.debug(
                "[CAPIO PASSAGE DEBUG] BiblePassage %s id=%s canonical_id=%s",
                "created" if created else "found",
                passage.pk,
                passage.canonical_id,
            )
                
            self.passage = passage
            logger.debug(
                "[CAPIO PASSAGE DEBUG] devotional.passage assigned devotional_id=%s passage_id=%s",
                self.pk,
                self.passage_id,
            )

    def clean(self):
        logger.debug(
            "[CAPIO PASSAGE DEBUG] clean() devotional_id=%s active=%s reviewed=%s passage_id=%s",
            self.pk,
            self.is_active,
            self.reviewed_by_human,
            self.passage_id,
        )
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
        logger.debug(
            "[CAPIO PASSAGE DEBUG] save() start devotional_id=%s update_fields=%s active=%s reviewed=%s passage_id=%s",
            self.pk,
            kwargs.get('update_fields'),
            self.is_active,
            self.reviewed_by_human,
            self.passage_id,
        )
        self.resolve_passage()

        if (self.is_active or self.reviewed_by_human) and not self.passage_id:
            logger.debug(
                "[CAPIO PASSAGE DEBUG] save() blocked devotional_id=%s because passage is missing",
                self.pk,
            )
            raise ValidationError({
                'passage': "O relacionamento 'passage' (BiblePassage) e obrigatorio para devocionais ativos ou revisados por humanos."
            })

        update_fields = kwargs.get('update_fields')
        if update_fields is not None and self.passage_id and 'passage' not in update_fields and 'passage_id' not in update_fields:
            kwargs['update_fields'] = set(update_fields)
            kwargs['update_fields'].add('passage')
            logger.debug(
                "[CAPIO PASSAGE DEBUG] save() appended passage to update_fields devotional_id=%s update_fields=%s",
                self.pk,
                kwargs['update_fields'],
            )

        logger.debug(
            "[CAPIO PASSAGE DEBUG] save() persist devotional_id=%s passage_id=%s",
            self.pk,
            self.passage_id,
        )
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} ({self.emotion.name})"

class UserDevotional(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='devotional_history')
    content = models.ForeignKey(DevotionalContent, on_delete=models.CASCADE, related_name='accessed_by')
    accessed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.content.title}"
