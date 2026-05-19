from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings

class User(AbstractUser):
    diocese = models.CharField(max_length=120, blank=True)
    notification_enabled = models.BooleanField(default=True)

    def __str__(self):
        return self.username

class UserFeedback(models.Model):
    RESPONSE_TYPE_CHOICES = [
        ('BIBLE', 'Bible'),
        ('DEVOTIONAL', 'Devotional'),
        ('REFLECTION', 'Reflection'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='feedbacks')
    response_type = models.CharField(max_length=20, choices=RESPONSE_TYPE_CHOICES)
    content_ref_id = models.PositiveIntegerField()
    helpful = models.BooleanField()
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'response_type', 'content_ref_id')

    def __str__(self):
        return f"Feedback {self.response_type} - {self.content_ref_id} by {self.user.username}"


class PushSubscription(models.Model):
    PREFERRED_TIME_CHOICES = [
        ('morning', 'Manhã'),
        ('evening', 'Noite'),
        ('any', 'Qualquer momento'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='push_subscriptions', 
        null=True, 
        blank=True
    )
    endpoint = models.URLField(max_length=500, unique=True)
    p256dh = models.CharField(max_length=255)
    auth = models.CharField(max_length=255)
    
    # Metadados e Preferências Contemplativas
    user_agent = models.TextField(blank=True, null=True)
    platform = models.CharField(max_length=100, blank=True, null=True)
    timezone = models.CharField(max_length=100, default='America/Sao_Paulo')
    preferred_time = models.CharField(
        max_length=20, 
        choices=PREFERRED_TIME_CHOICES, 
        default='morning'
    )
    enabled = models.BooleanField(default=True)
    last_sent_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        owner = self.user.username if self.user else "Anonymous"
        return f"Push Subscription ({owner}) - {self.endpoint[:30]}..."
