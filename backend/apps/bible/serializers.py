from rest_framework import serializers
from .models import PassageExplanation

class ExplainRequestSerializer(serializers.Serializer):
    reference = serializers.CharField(max_length=150)

class PassageExplanationSerializer(serializers.ModelSerializer):
    scripture_text = serializers.CharField(source='passage.text_original', read_only=True)

    class Meta:
        model = PassageExplanation
        fields = (
            'id',
            'reference_display',
            'scripture_text',
            'simple_explanation',
            'biblical_context',
            'practical_application',
            'spiritual_reflection',
            'optional_prayer',
            'ai_generated',
            'created_at'
        )

