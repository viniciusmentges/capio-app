from rest_framework import serializers
from .models import DailyReflection, UserReflectionResponse

class RespondRequestSerializer(serializers.Serializer):
    response_text = serializers.CharField(required=True)

class DailyReflectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyReflection
        fields = (
            'id', 'date', 'passage', 'title', 'scripture_reference', 
            'scripture_text', 'reflection_body', 'guiding_question', 
            'closing_prayer', 'ai_generated'
        )

class UserReflectionResponseSerializer(serializers.ModelSerializer):
    reflection = DailyReflectionSerializer()

    class Meta:
        model = UserReflectionResponse
        fields = ('reflection', 'response_text', 'created_at')
