from django.db import models
from django.conf import settings

class AIRequest(models.Model):
    REQUEST_TYPE_CHOICES = [
        ('bible', 'Bible'),
        ('devotional', 'Devotional'),
        ('reflection', 'Reflection'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('error', 'Error'),
        ('blocked', 'Blocked'),
    ]

    request_type = models.CharField(max_length=20, choices=REQUEST_TYPE_CHOICES)
    input_hash = models.CharField(max_length=64)
    input_data = models.JSONField(default=dict)
    output_data = models.JSONField(default=dict)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    flagged_for_review = models.BooleanField(default=False)
    duration_ms = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.request_type} - {self.status} - {self.input_hash[:8]}"

class GeneratedResponse(models.Model):
    RESPONSE_TYPE_CHOICES = [
        ('BIBLE', 'Bible'),
        ('DEVOTIONAL', 'Devotional'),
        ('REFLECTION', 'Reflection'),
    ]
    FILTER_STATUS_CHOICES = [
        ('clean', 'Clean'),
        ('soft_flagged', 'Soft Flagged'),
        ('hard_blocked', 'Hard Blocked'),
    ]

    response_type = models.CharField(max_length=20, choices=RESPONSE_TYPE_CHOICES)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='generated_responses')
    ai_request = models.ForeignKey(AIRequest, on_delete=models.SET_NULL, null=True, blank=True, related_name='generated_responses')
    filter_status = models.CharField(max_length=20, choices=FILTER_STATUS_CHOICES)
    content_ref_id = models.PositiveIntegerField()
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['response_type', 'content_ref_id']),
            models.Index(fields=['user', 'response_type', 'created_at']),
        ]

    def __str__(self):
        return f"Response {self.response_type} - Ref {self.content_ref_id}"
