from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from apps.users.models import UserFeedback
from apps.bible.models import PassageExplanation

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
