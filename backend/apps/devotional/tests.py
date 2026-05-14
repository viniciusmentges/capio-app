from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from apps.devotional.models import Emotion

User = get_user_model()

class DevotionalTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.force_authenticate(user=self.user)
        Emotion.objects.create(name="Ansioso", slug="ansioso")

    def test_get_emotions(self):
        url = '/api/devotional/emotions/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) > 0)
        self.assertEqual(response.data[0]['slug'], 'ansioso')

    def test_get_devotional_by_emotion(self):
        url = '/api/devotional/by-emotion/'
        data = {'emotion_slug': 'ansioso'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('title', response.data)

    def test_get_devotional_not_found(self):
        url = '/api/devotional/by-emotion/'
        data = {'emotion_slug': 'inexistente'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
