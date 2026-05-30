from unittest.mock import patch
from django.utils import timezone
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from django.core import mail
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from apps.users.models import UserFeedback, PushSubscription
from apps.users.tasks import should_send_push
from apps.bible.models import PassageExplanation
from apps.ai_core.models import GeneratedResponse
from apps.reflection.models import DailyReflection

User = get_user_model()

class AuthTests(APITestCase):
    def test_register_user(self):
        url = '/api/auth/register/'
        data = {'username': 'testuser', 'password': 'testpassword', 'email': 'test@test.com'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username='testuser').exists())

    def test_login_user(self):
        User.objects.create_user(username='testuser', password='testpassword')
        url = '/api/auth/login/'
        data = {'username': 'testuser', 'password': 'testpassword'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_me_endpoint(self):
        user = User.objects.create_user(username='testuser', password='testpassword')
        url = '/api/auth/login/'
        data = {'username': 'testuser', 'password': 'testpassword'}
        response = self.client.post(url, data, format='json')
        token = response.data['access']

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        me_url = '/api/auth/me/'
        me_response = self.client.get(me_url)
        self.assertEqual(me_response.status_code, status.HTTP_200_OK)
        self.assertEqual(me_response.data['username'], 'testuser')

class FeedbackTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.force_authenticate(user=self.user)
        self.passage = PassageExplanation.objects.create(
            reference_normalized="jo 3:16",
            reference_display="Jo 3:16",
            explanation="Teste"
        )

    def test_submit_feedback(self):
        url = '/api/feedback/'
        data = {
            'response_type': 'BIBLE',
            'content_ref_id': self.passage.id,
            'helpful': True,
            'comment': 'Gostei'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(UserFeedback.objects.filter(user=self.user, response_type='BIBLE', content_ref_id=self.passage.id).exists())

class PushSuppressionTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='pushuser', password='testpassword')
        self.subscription = PushSubscription.objects.create(
            user=self.user,
            endpoint="https://example.com/push-endpoint",
            p256dh="some-dh-key",
            auth="some-auth-key",
            timezone="America/Sao_Paulo",
            preferred_time="evening",
            enabled=True
        )

    def test_should_not_send_push_if_inactive_for_5_days(self):
        # Sem acessos recentes
        self.assertFalse(should_send_push(self.user, self.subscription))

    def test_should_send_push_if_recent_access(self):
        # Acesso recente genérico
        GeneratedResponse.objects.create(
            response_type='REFLECTION',
            user=self.user,
            content_ref_id=999,
            filter_status='clean',
            metadata={"type": "user_access"}
        )
        # Vamos fingir que estamos na janela noturna local (19h-22h)
        with patch('django.utils.timezone.localtime') as mock_localtime:
            import datetime
            # Mockando 20:00 (janela noturna válida)
            mock_localtime.return_value = timezone.make_aware(
                datetime.datetime(2026, 5, 24, 20, 0, 0),
                timezone=timezone.get_current_timezone()
            )
            # Sem leitura de reflexão de hoje feita
            self.assertTrue(should_send_push(self.user, self.subscription))

    def test_should_suppress_evening_push_if_read_today(self):
        # Acesso recente genérico para passar na regra de ausência de 5 dias
        GeneratedResponse.objects.create(
            response_type='REFLECTION',
            user=self.user,
            content_ref_id=999,
            filter_status='clean',
            metadata={"type": "user_access"}
        )
        
        with patch('django.utils.timezone.localtime') as mock_localtime:
            import datetime
            # Mockando 2026-05-24 20:00:00 (dentro da janela noturna local)
            mock_localtime.return_value = timezone.make_aware(
                datetime.datetime(2026, 5, 24, 20, 0, 0),
                timezone=timezone.get_current_timezone()
            )
            
            # Reflexão de hoje gerada e lida (com a mesma data mockada)
            today = mock_localtime.return_value.date()
            reflection = DailyReflection.objects.create(
                date=today,
                title="Hoje",
                reflection_body="Corpo hoje",
                scripture_reference="Salmo 23:1",
                share_quote="Frase"
            )
            # Registrar leitura da reflexão de hoje
            GeneratedResponse.objects.create(
                response_type='REFLECTION',
                user=self.user,
                content_ref_id=reflection.id,
                filter_status='clean',
                metadata={"type": "user_access"}
            )
            
            # Deve silenciar já que a reflexão de hoje já foi lida!
            self.assertFalse(should_send_push(self.user, self.subscription))

class PasswordResetTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser2', email='test@test.com', password='testpassword')
        self.reset_url = '/api/auth/password-reset/'
        self.confirm_url = '/api/auth/password-reset/confirm/'

    def test_request_reset_existing_email(self):
        response = self.client.post(self.reset_url, {'email': 'test@test.com'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Se este e-mail estiver cadastrado, enviaremos instruções para redefinir sua senha.')
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Redefinir senha na CAPIO', mail.outbox[0].subject)

    def test_request_reset_non_existing_email(self):
        response = self.client.post(self.reset_url, {'email': 'nobody@test.com'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Se este e-mail estiver cadastrado, enviaremos instruções para redefinir sua senha.')
        self.assertEqual(len(mail.outbox), 0)

    def test_confirm_reset_valid_token(self):
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = PasswordResetTokenGenerator().make_token(self.user)
        
        data = {
            'uid': uid,
            'token': token,
            'new_password': 'NewPassword123!',
            'confirm_password': 'NewPassword123!'
        }
        response = self.client.post(self.confirm_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify password changed
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('NewPassword123!'))

    def test_confirm_reset_invalid_token(self):
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        data = {
            'uid': uid,
            'token': 'invalid-token',
            'new_password': 'NewPassword123!',
            'confirm_password': 'NewPassword123!'
        }
        response = self.client.post(self.confirm_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('token', response.data)

    def test_confirm_reset_weak_password(self):
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = PasswordResetTokenGenerator().make_token(self.user)
        
        data = {
            'uid': uid,
            'token': token,
            'new_password': '123',
            'confirm_password': '123'
        }
        response = self.client.post(self.confirm_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('new_password', response.data)

    def test_confirm_reset_mismatched_passwords(self):
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = PasswordResetTokenGenerator().make_token(self.user)
        
        data = {
            'uid': uid,
            'token': token,
            'new_password': 'NewPassword123!',
            'confirm_password': 'DifferentPassword123!'
        }
        response = self.client.post(self.confirm_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('confirm_password', response.data)

