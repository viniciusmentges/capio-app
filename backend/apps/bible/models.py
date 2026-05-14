from django.db import models

class BiblePassage(models.Model):
    canonical_id = models.CharField(max_length=100, unique=True, db_index=True) # e.g. PSA.23
    book_name = models.CharField(max_length=100)
    chapter = models.IntegerField()
    verses = models.CharField(max_length=100, null=True, blank=True)
    text_original = models.TextField()
    translation = models.CharField(max_length=50, default="NVI")
    language = models.CharField(max_length=10, default="pt")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.canonical_id} ({self.translation})"

class PassageExplanation(models.Model):
    passage = models.ForeignKey(BiblePassage, on_delete=models.CASCADE, related_name='explanations', null=True, blank=True)
    reference_normalized = models.CharField(max_length=100, unique=True, db_index=True)
    reference_display = models.CharField(max_length=150)
    explanation = models.TextField(blank=True, default="")
    simple_explanation = models.TextField(blank=True, default="")
    biblical_context = models.TextField(blank=True, default="")
    practical_application = models.TextField(blank=True, default="")
    spiritual_reflection = models.TextField(blank=True, default="")
    optional_prayer = models.TextField(blank=True, default="")
    ai_generated = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.reference_display
