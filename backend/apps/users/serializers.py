from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from apps.users.models import UserFeedback, PushSubscription

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'diocese', 'notification_enabled')
        read_only_fields = ('id',)

class UserPushPreferencesSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('push_daily_reminder', 'push_reminder_time', 'push_timezone')
        read_only_fields = ()

class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

class PasswordResetConfirmSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "As senhas não coincidem."})
        
        try:
            validate_password(data['new_password'])
        except DjangoValidationError as e:
            raise serializers.ValidationError({"new_password": list(e.messages)})
            
        try:
            uid = force_str(urlsafe_base64_decode(data['uid']))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise serializers.ValidationError({"token": "Link de recuperação inválido ou expirado."})
            
        if not PasswordResetTokenGenerator().check_token(user, data['token']):
            raise serializers.ValidationError({"token": "Link de recuperação inválido ou expirado."})
            
        return data

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


class PushSubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PushSubscription
        fields = (
            'id', 'endpoint', 'p256dh', 'auth', 
            'user_agent', 'platform', 'timezone', 
            'preferred_time', 'enabled'
        )
        read_only_fields = ('id',)
