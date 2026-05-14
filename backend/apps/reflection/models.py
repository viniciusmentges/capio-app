from django.db import models
from django.conf import settings

class DailyReflection(models.Model):
    date = models.DateField(unique=True)
    passage = models.ForeignKey('bible.BiblePassage', on_delete=models.SET_NULL, null=True, blank=True, related_name='daily_reflections')
    title = models.CharField(max_length=180)
    scripture_reference = models.CharField(max_length=150)
    scripture_text = models.TextField()
    reflection_body = models.TextField()
    guiding_question = models.TextField()
    closing_prayer = models.TextField()
    ai_generated = models.BooleanField(default=False)

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
