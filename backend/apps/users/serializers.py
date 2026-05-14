from rest_framework import serializers
from django.contrib.auth import get_user_model
from apps.users.models import UserFeedback

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'diocese', 'notification_enabled')
        read_only_fields = ('id',)

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'diocese')

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
            diocese=validated_data.get('diocese', '')
        )
        return user

class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserFeedback
        fields = ('response_type', 'content_ref_id', 'helpful', 'comment')
