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
    is_active = models.BooleanField(default=True)
    ai_generated = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.emotion.name})"

class UserDevotional(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='devotional_history')
    content = models.ForeignKey(DevotionalContent, on_delete=models.CASCADE, related_name='accessed_by')
    accessed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.content.title}"
