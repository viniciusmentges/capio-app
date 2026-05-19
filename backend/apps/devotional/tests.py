from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from apps.devotional.models import Emotion, DevotionalContent, UserDevotional

User = get_user_model()

class DevotionalTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.force_authenticate(user=self.user)
        self.emotion = Emotion.objects.create(name="Ansioso", slug="ansioso")

    def test_get_emotions(self):
        url = '/api/devotional/emotions/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) > 0)
        self.assertEqual(response.data[0]['slug'], 'ansioso')

    def test_get_devotional_by_emotion(self):
        # Criar pelo menos um devocional para evitar chamar IA no teste simples
        DevotionalContent.objects.create(
            emotion=self.emotion,
            title="Devocional 1",
            scripture_reference="Salmo 23",
            scripture_text="O Senhor é o meu pastor",
            reflection="Reflexão",
            prayer="Oração",
            is_active=True
        )
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

    def test_devotional_rotation_and_sliding_window(self):
        # 1. Criar um pool de 8 devocionais no banco para testar a regra K = 5
        devotionals = []
        for i in range(8):
            d = DevotionalContent.objects.create(
                emotion=self.emotion,
                title=f"Devocional {i+1}",
                scripture_reference=f"Ref {i+1}",
                scripture_text=f"Texto {i+1}",
                reflection=f"Reflexão {i+1}",
                prayer=f"Oração {i+1}",
                is_active=True
            )
            devotionals.append(d)

        url = '/api/devotional/by-emotion/'
        data = {'emotion_slug': 'ansioso'}

        # 2. Fazer 5 requisições consecutivas
        seen_titles = []
        for step in range(5):
            response = self.client.post(url, data, format='json')
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            title = response.data['title']
            seen_titles.append(title)
            
            # Verificar se o histórico UserDevotional está registrando a leitura e aumentando
            history_count = UserDevotional.objects.filter(user=self.user, content__emotion=self.emotion).count()
            self.assertEqual(history_count, step + 1)

        # Como temos 8 itens e excluímos os K recentes (K = max(1, min(5, 8-3)) = 5):
        # As primeiras 5 leituras não podem conter nenhuma repetição, pois priorizamos inéditos e excluímos recentes!
        self.assertEqual(len(set(seen_titles)), 5, "Houve repetição indevida nas primeiras 5 leituras!")

        # 3. Fazer a 6ª requisição
        # A 6ª leitura não pode ser igual a NENHUMA das últimas 5 (todas as anteriores lidas)
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        sixth_title = response.data['title']

        # Os últimos 5 títulos vistos são seen_titles (pois a janela K é 5)
        # O 6º título não pode estar entre as últimas 5 leituras!
        self.assertNotIn(sixth_title, seen_titles, "O 6º devocional repetiu um dos últimos 5 vistos!")

        # 4. Fazer 10 requisições seguidas para validar a imunidade a repetição consecutiva (Back-to-Back)
        last_title = sixth_title
        for step in range(10):
            response = self.client.post(url, data, format='json')
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            current_title = response.data['title']
            self.assertNotEqual(current_title, last_title, f"Houve repetição idêntica consecutiva no passo {step}!")
            last_title = current_title

