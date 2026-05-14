from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

User = get_user_model()

class ReflectionTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.force_authenticate(user=self.user)

    def test_get_today_reflection(self):
        url = '/api/reflection/today/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('reflection', response.data)

    def test_respond_reflection(self):
        # Primeiro, buscamos a reflexão de hoje
        self.client.get('/api/reflection/today/')

        url = '/api/reflection/today/respond/'
        data = {'response_text': 'Minha resposta'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Verificamos se foi salvo corretamente
        get_response = self.client.get('/api/reflection/today/')
        self.assertEqual(get_response.data['user_response'], 'Minha resposta')
