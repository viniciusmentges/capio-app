from rest_framework import serializers
from .models import DailyReflection, UserReflectionResponse

class RespondRequestSerializer(serializers.Serializer):
    response_text = serializers.CharField(required=True)

class DailyReflectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyReflection
        fields = (
            'id', 'public_id', 'date', 'passage', 'title', 'scripture_reference', 
            'scripture_text', 'reflection_body', 'main_truth', 'daily_companion',
            'guiding_question', 'closing_prayer', 'share_quote', 'share_text', 
            'share_bg_image', 'ai_generated'
        )

class UserReflectionResponseSerializer(serializers.ModelSerializer):
    reflection = DailyReflectionSerializer()

    class Meta:
        model = UserReflectionResponse
        fields = ('reflection', 'response_text', 'created_at')
