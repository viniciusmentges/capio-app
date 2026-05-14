from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from apps.bible.models import PassageExplanation

User = get_user_model()

class BibleTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.force_authenticate(user=self.user)

    def test_explain_passage(self):
        url = reverse('explain')
        data = {'reference': 'João 3:16'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('simple_explanation', response.data)
        self.assertIn('biblical_context', response.data)
        self.assertIn('practical_application', response.data)
        self.assertIn('spiritual_reflection', response.data)
        self.assertIn('optional_prayer', response.data)
        self.assertIn('reference_display', response.data)
        self.assertNotIn('explanation', response.data) # Garante que legacy não volta

    def test_explain_passage_limits(self):
        # Testa o comportamento de truncamento manual, injetando uma mock string longa via ai_service
        from unittest.mock import patch
        long_text = "A" * 950 # simple_explanation limite é 900, 950 entra na zona de truncamento (< 1.2 * 900 = 1080)
        huge_text = "B" * 1200 # > 1080, entra na zona de fallback
        
        mock_response = {
            "simple_explanation": long_text,
            "biblical_context": "Contexto curto",
            "practical_application": "Aplicação",
            "spiritual_reflection": "Reflexão",
            "optional_prayer": huge_text,
            "ai_generated": True
        }
        
        with patch('services.ai.mock.MockAIService.explain_passage', return_value=mock_response):
            url = reverse('explain')
            data = {'reference': 'Marcos 1:1'}
            response = self.client.post(url, data, format='json')
            
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            # Verifica truncamento: longo (mas não huge) trunca e bota ...
            self.assertTrue(response.data['simple_explanation'].endswith('...'))
            self.assertEqual(len(response.data['simple_explanation']), 900)
            
            # Verifica fallback: huge text > 1.2*limit aciona fallback mockado
            self.assertEqual(response.data['optional_prayer'], "Oração mockada.")
            self.assertEqual(response.data['biblical_context'], "Contexto curto")

    def test_hard_block_passage(self):
        url = reverse('explain')
        data = {'reference': 'feitiçaria'} # Termo presente em HARD_BLOCK_TERMS
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        self.assertEqual(response.data['error'], 'content_blocked')

    def test_bible_history(self):
        PassageExplanation.objects.create(
            reference_normalized='jo 3:16', 
            reference_display='João 3:16', 
            simple_explanation='Teste'
        )
        url = '/api/bible/history/'
        # Historico inicialmente vazio pois dependemos do GeneratedResponse, precisamos executar explain antes
        self.client.post('/api/bible/explain/', {'reference': 'João 3:16'}, format='json')
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) > 0)
