from rest_framework import serializers
from .models import PassageExplanation

from services.bible.normalization import NormalizationService

class ExplainRequestSerializer(serializers.Serializer):
    reference = serializers.CharField(max_length=150)

    def validate_reference(self, value):
        if not NormalizationService.is_valid_reference(value):
            raise serializers.ValidationError("Este espaço acolhe uma passagem da Escritura. Para caminhar com o que você está sentindo, procure o devocional por emoção.")
        return value

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

