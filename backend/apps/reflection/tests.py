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
        self.assertIn('night_word', response.data)
        self.assertIn('night_prayer', response.data)

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

    def test_spiritual_journey_0_readings(self):
        url = '/api/reflection/spiritual-journey/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['show_journey'])
        self.assertEqual(response.data['journey_text'], '')

    def test_spiritual_journey_1_reading(self):
        from apps.ai_core.models import GeneratedResponse
        GeneratedResponse.objects.create(
            user=self.user,
            response_type='REFLECTION',
            content_ref_id=1,
            filter_status='clean'
        )
        url = '/api/reflection/spiritual-journey/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['show_journey'])
        self.assertEqual(response.data['read_count'], 1)

    def test_spiritual_journey_2_readings(self):
        from apps.ai_core.models import GeneratedResponse
        GeneratedResponse.objects.create(user=self.user, response_type='REFLECTION', content_ref_id=1, filter_status='clean')
        GeneratedResponse.objects.create(user=self.user, response_type='REFLECTION', content_ref_id=2, filter_status='clean')
        url = '/api/reflection/spiritual-journey/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['show_journey'])
        self.assertEqual(response.data['read_count'], 2)

    def test_spiritual_journey_3_readings_eligible(self):
        from apps.ai_core.models import GeneratedResponse
        from apps.reflection.models import DailyReflection
        from unittest.mock import patch
        from datetime import datetime

        # Cria 3 leituras válidas e traduzíveis
        real_today = timezone.localtime()
        today_date = real_today.date()
        for i, theme in enumerate(["esperanca", "contemplacao", "esperanca"]):
            ref = DailyReflection.objects.create(
                date=today_date - timedelta(days=i),
                title=f"Ref {i}",
                theme_key=theme,
                scripture_reference="Salmo",
                scripture_text="Texto",
                reflection_body="Corpo",
                closing_prayer="Oracao",
            )
            GeneratedResponse.objects.create(user=self.user, response_type='REFLECTION', content_ref_id=ref.id, filter_status='clean')

        url = '/api/reflection/spiritual-journey/'
        
        # Moca o datetime para garantir que ((day + user.id) % 3 == 0) seja True
        target_day = 3 - (self.user.id % 3)
        if target_day <= 0: target_day += 3
        
        mock_dt = real_today.replace(day=target_day)
        
        with patch('django.utils.timezone.localtime', return_value=mock_dt):
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertTrue(response.data['show_journey'])
            self.assertEqual(response.data['read_count'], 3)
            self.assertIn('esperança viva', response.data['journey_text'])
            self.assertIn('silêncio e quietude', response.data['journey_text'])

    def test_night_view_returns_new_fields(self):
        # Garante a criação de hoje com os novos campos preenchidos
        today = timezone.localtime().date()
        DailyReflection.objects.get_or_create(
            date=today,
            defaults={
                "title": "Hoje",
                "reflection_body": "Hoje corpo",
                "scripture_reference": "Salmo 23:2",
                "scripture_text": "Texto",
                "share_quote": "Quote dia",
                "night_word": "Nova palavra da noite",
                "night_prayer": "Nova oração noturna"
            }
        )
        url = '/api/reflection/night/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('night_word', response.data)
        self.assertIn('night_prayer', response.data)
        self.assertEqual(response.data['night_word'], "Nova palavra da noite")
        self.assertEqual(response.data['night_prayer'], "Nova oração noturna")

    def test_night_view_legacy_fallback(self):
        # Testa uma reflexão antiga sem campos noturnos preenchidos
        today = timezone.localtime().date()
        DailyReflection.objects.get_or_create(
            date=today,
            defaults={
                "title": "Hoje",
                "reflection_body": "Hoje corpo",
                "scripture_reference": "Salmo 23:2",
                "scripture_text": "Texto",
                "share_quote": "Quote dia",
                "night_word": "",
                "night_prayer": ""
            }
        )
        url = '/api/reflection/night/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['night_word'], "Há um repouso silencioso que nos aguarda no fim de tudo.")
        self.assertEqual(response.data['night_prayer'], "Senhor, entrego este dia em tuas mãos. Que a noite traga repouso e a certeza de que não estou só. Amém.")

    def test_reflection_service_anti_repetition_fallback(self):
        from services.reflection.reflection_service import ReflectionService
        from apps.ai_core.models import AIRequest
        from unittest.mock import patch

        # Simula resposta falha da IA onde night_word copia share_quote e night_prayer copia closing_prayer
        mock_ai_response = {
            "title": "Teste",
            "scripture_reference": "Joao 1",
            "scripture_text": "No inicio...",
            "reflection_body": "Corpo da reflexão",
            "share_quote": "A mesma frase",
            "closing_prayer": "A mesma oração",
            "night_word": "A mesma frase",
            "night_prayer": "A mesma oração",
            "ai_generated": True
        }

        with patch('services.ai.anthropic.AnthropicAIService.generate_reflection', return_value=mock_ai_response):
            today = timezone.localtime().date()
            reflection = ReflectionService.warmup_reflection(target_date=today)
            
            # Garante que o fallback protegeu o banco de dados contra repetição
            self.assertNotEqual(reflection.night_word, "A mesma frase")
            self.assertEqual(reflection.night_word, "Há um repouso silencioso que nos aguarda no fim de tudo.")
            
            self.assertNotEqual(reflection.night_prayer, "A mesma oração")
            self.assertEqual(reflection.night_prayer, "Senhor, entrego este dia em tuas mãos. Que a noite traga repouso e a certeza de que não estou só. Amém.")
