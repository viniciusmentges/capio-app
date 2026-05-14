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
            'id', 'passage', 'title', 'scripture_reference', 'scripture_text', 
            'reflection', 'practical_application', 'guiding_question', 
            'prayer', 'ai_generated', 'created_at'
        )


class UserDevotionalSerializer(serializers.ModelSerializer):
    content = DevotionalContentSerializer()

    class Meta:
        model = UserDevotional
        fields = ('content', 'accessed_at')
