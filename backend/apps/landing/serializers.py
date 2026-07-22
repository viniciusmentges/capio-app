from rest_framework import serializers
from .models import LandingScreenshot, Lead

class LandingScreenshotSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = LandingScreenshot
        fields = ['key', 'title', 'image_url', 'alt_text', 'sort_order']

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and hasattr(obj.image, 'url'):
            if request is not None:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None

class LeadSerializer(serializers.ModelSerializer):
    consent_communications = serializers.BooleanField(source='consent_given')

    class Meta:
        model = Lead
        fields = [
            'email', 'name', 'source', 'consent_communications',
            'utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'utm_term'
        ]
        
    def validate_consent_communications(self, value):
        if not value:
            raise serializers.ValidationError("O consentimento é obrigatório.")
        return value
