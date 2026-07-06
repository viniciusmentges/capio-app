from rest_framework import serializers
from .models import Emotion, DevotionalContent, UserDevotional

class EmotionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Emotion
        fields = ('name', 'slug', 'icon')

class DevotionalRequestSerializer(serializers.Serializer):
    emotion_slug = serializers.CharField(max_length=80)

class DevotionalContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = DevotionalContent
        fields = (
            'id', 'public_id', 'passage', 'title', 'scripture_reference', 'scripture_text', 
            'reflection', 'practical_application', 'guiding_question', 
            'prayer', 'share_quote', 'emotional_theme', 'main_truth', 'daily_companion',
            'share_text', 'share_bg_image', 'ai_generated', 'created_at'
        )


class UserDevotionalSerializer(serializers.ModelSerializer):
    content = DevotionalContentSerializer()

    class Meta:
        model = UserDevotional
        fields = ('content', 'accessed_at')
