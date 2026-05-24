from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.test import override_settings
from datetime import date, timedelta

from apps.reflection.models import DailyReflection
from services.reflection.editorial_analytics import (
    get_theme_distribution,
    get_scripture_coverage,
    get_saturation_alerts,
    get_editorial_timeline,
    get_emotional_theme_frequency,
    generate_editorial_report
)

User = get_user_model()

class ReflectionTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.staff_user = User.objects.create_user(username='staffuser', password='staffpassword', is_staff=True)
        self.client.force_authenticate(user=self.user)

    def test_get_today_reflection(self):
        url = '/api/reflection/today/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('reflection', response.data)

    def test_respond_reflection(self):
        # Primeiro, buscamos a reflexão de hoje para garantir a criação
        self.client.get('/api/reflection/today/')

        url = '/api/reflection/today/respond/'
        data = {'response_text': 'Minha resposta'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Verificamos se foi salvo corretamente
        get_response = self.client.get('/api/reflection/today/')
        self.assertEqual(get_response.data['user_response'], 'Minha resposta')

    def test_editorial_analytics_theme_distribution(self):
        today = timezone.localtime().date()
        # Criamos algumas reflexões no passado recente com eixos específicos
        DailyReflection.objects.create(
            date=today - timedelta(days=2),
            title="Reflexão A",
            reflection_body="Corpo A",
            theme_key="esperanca",
            emotional_theme="Esperança, Silêncio",
            scripture_reference="Salmos 23:1",
            share_quote="Frase A"
        )
        DailyReflection.objects.create(
            date=today - timedelta(days=1),
            title="Reflexão B",
            reflection_body="Corpo B",
            theme_key="sofrimento",
            emotional_theme="Sofrimento, Dor",
            scripture_reference="Salmos 88:1",
            share_quote="Frase B"
        )
        DailyReflection.objects.create(
            date=today,
            title="Reflexão C",
            reflection_body="Corpo C",
            theme_key="esperanca",
            emotional_theme="Esperança, Luz",
            scripture_reference="Romanos 5:5",
            share_quote="Frase C"
        )

        dist = get_theme_distribution(days=7)
        self.assertEqual(dist["total_analyzed"], 3)
        self.assertEqual(dist["distribution"]["esperanca"]["count"], 2)
        self.assertEqual(dist["distribution"]["sofrimento"]["count"], 1)
        self.assertAlmostEqual(dist["distribution"]["esperanca"]["percentage"], 66.67, places=1)

    def test_editorial_analytics_scripture_coverage(self):
        today = timezone.localtime().date()
        DailyReflection.objects.create(
            date=today - timedelta(days=2),
            title="Reflexão A",
            reflection_body="Corpo A",
            theme_key="esperanca",
            emotional_theme="Esperança",
            scripture_reference="Salmos 23:1",
            share_quote="Frase A"
        )
        DailyReflection.objects.create(
            date=today - timedelta(days=1),
            title="Reflexão B",
            reflection_body="Corpo B",
            theme_key="sofrimento",
            emotional_theme="Sofrimento",
            scripture_reference="Mateus 6:33",
            share_quote="Frase B"
        )

        coverage = get_scripture_coverage(days=7)
        self.assertEqual(coverage["total_analyzed"], 2)
        self.assertEqual(coverage["book_frequency"]["Salmos"], 1)
        self.assertEqual(coverage["book_frequency"]["Mateus"], 1)
        self.assertEqual(coverage["salms_percentage"], 50.0)
        self.assertEqual(coverage["nt_percentage"], 50.0)
        self.assertEqual(coverage["ot_percentage"], 50.0)

    def test_editorial_analytics_saturation_alerts(self):
        today = timezone.localtime().date()
        
        # 1. Testar saturação de share_quotes semanticamente parecidos via Jaccard
        DailyReflection.objects.create(
            date=today - timedelta(days=1),
            title="Reflexão Similar A",
            reflection_body="Corpo",
            theme_key="esperanca",
            emotional_theme="Esperança",
            scripture_reference="Salmos 23:1",
            share_quote="O Senhor é o meu pastor, e nada me faltará hoje."
        )
        DailyReflection.objects.create(
            date=today,
            title="Reflexão Similar B",
            reflection_body="Corpo",
            theme_key="esperanca",
            emotional_theme="Esperança",
            scripture_reference="Salmos 23:2",
            share_quote="O Senhor é meu pastor, e nada me faltará de modo algum."
        )

        alerts = get_saturation_alerts(days=7)
        # Deve ter gerado o alerta de similaridade semântica (Jaccard > 0.4)
        semantic_alerts = [a for a in alerts if a["category"] == "semantic_similarity"]
        self.assertTrue(len(semantic_alerts) >= 1)
        self.assertIn("similaridade vocabular", semantic_alerts[0]["message"])

    def test_editorial_insights_endpoint_permissions(self):
        url = '/api/reflection/editorial-insights/'

        # 1. Não autenticado -> 401
        self.client.logout()
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # 2. Autenticado mas sem staff -> 403
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # 3. Autenticado e staff -> 200
        self.client.force_authenticate(user=self.staff_user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("theme_distribution", response.data)
        self.assertIn("emotional_distribution", response.data)
        self.assertIn("scripture_coverage", response.data)
        self.assertIn("saturation_alerts", response.data)
        self.assertIn("timeline", response.data)
        self.assertIn("report", response.data)

    @override_settings(DEBUG=True)
    def test_editorial_insights_endpoint_debug_mode(self):
        url = '/api/reflection/editorial-insights/'
        # Em modo DEBUG=True, mesmo usuário comum (não staff) deve conseguir ler
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_night_view(self):
        # Garante a criação da reflexão de hoje
        self.client.get('/api/reflection/today/')
        url = '/api/reflection/night/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('share_quote', response.data)
        self.assertIn('closing_prayer', response.data)

    def test_liturgical_archive_view(self):
        # Garante a criação de hoje e cria outra no passado
        self.client.get('/api/reflection/today/')
        today = timezone.localtime().date()
        DailyReflection.objects.get_or_create(
            date=today - timedelta(days=1),
            defaults={
                "title": "Ontem",
                "reflection_body": "Ontem corpo",
                "scripture_reference": "Salmo 23:2",
                "scripture_text": "Texto",
                "share_quote": "Quote ontem"
            }
        )
        url = '/api/reflection/liturgical-archive/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) >= 2)

    def test_spiritual_journey_view(self):
        # Garante leituras para contar temas
        self.client.get('/api/reflection/today/')
        url = '/api/reflection/spiritual-journey/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('journey_text', response.data)
        self.assertIn('top_themes', response.data)


