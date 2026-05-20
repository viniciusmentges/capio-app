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
            share_quote="O Senhor é pastor.",
            is_active=True,
            reviewed_by_human=True
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
                share_quote=f"Frase {i+1}",
                is_active=True,
                reviewed_by_human=True
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

    def test_reviewed_by_human_filter(self):
        # 1. Criar um devocional com reviewed_by_human=False
        unreviewed = DevotionalContent.objects.create(
            emotion=self.emotion,
            title="Devocional Não Revisado",
            scripture_reference="Ref",
            scripture_text="Texto",
            reflection="Reflexão",
            prayer="Oração",
            share_quote="Frase",
            is_active=True,
            reviewed_by_human=False
        )

        url = '/api/devotional/by-emotion/'
        data = {'emotion_slug': 'ansioso'}
        
        # Como o único devocional não está revisado, o endpoint de rotação deve disparar IA de background (Mock)
        # e NÃO retornar este devocional não revisado.
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(response.data['title'], "Devocional Não Revisado")

    def test_editorial_generate_permissions(self):
        url = '/api/devotional/editorial/generate/'
        data = {'emotion_slug': 'ansioso', 'tone_or_direction': 'contemplativo'}

        # 1. Usuário comum logado (deve retornar 403 Forbidden)
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # 2. Usuário staff logado (deve retornar 200 OK)
        self.user.is_staff = True
        self.user.save()
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('title', response.data)
        self.assertIn('share_quote', response.data)
        self.assertIn('emotional_theme', response.data)

    def test_devotional_resolves_passage_automatically(self):
        # 1. Criar novo devocional com scripture_reference válida
        dev = DevotionalContent.objects.create(
            emotion=self.emotion,
            title="Meditação sobre o amparo",
            scripture_reference="Filipenses 4:6",
            scripture_text="Não andeis ansiosos...",
            reflection="Espera e silêncio.",
            prayer="Pai, repouso em ti.",
            share_quote="Não andeis ansiosos.",
            is_active=True,
            reviewed_by_human=True
        )
        self.assertIsNotNone(dev.passage)
        self.assertEqual(dev.passage.canonical_id, "PHP.4.6")

    def test_active_without_passage_fails(self):
        from django.core.exceptions import ValidationError
        # 1. Tentar criar devocional ativo com scripture_reference vazia (que não resolve passage)
        dev = DevotionalContent(
            emotion=self.emotion,
            title="Sem passagem",
            scripture_reference="",
            scripture_text="",
            reflection="Texto",
            prayer="Oração",
            share_quote="Frase",
            is_active=True,
            reviewed_by_human=False
        )
        with self.assertRaises(ValidationError):
            dev.full_clean()

    def test_reviewed_by_human_without_passage_fails(self):
        from django.core.exceptions import ValidationError
        # 2. Tentar criar devocional revisado com scripture_reference vazia (que não resolve passage)
        dev = DevotionalContent(
            emotion=self.emotion,
            title="Revisado sem passagem",
            scripture_reference="",
            scripture_text="",
            reflection="Texto",
            prayer="Oração",
            share_quote="Frase",
            is_active=False,
            reviewed_by_human=True
        )
        with self.assertRaises(ValidationError):
            dev.full_clean()

    def test_backfill_management_command(self):
        from django.core.management import call_command
        # 1. Criar devocional rascunho (inativo e não revisado) para contornar a obrigatoriedade
        dev = DevotionalContent.objects.create(
            emotion=self.emotion,
            title="Devocional Antigo Órfão",
            scripture_reference="Salmos 34:18",
            scripture_text="O Senhor está perto...",
            reflection="O silêncio do Senhor...",
            prayer="Oração antiga.",
            share_quote="O Senhor está perto.",
            is_active=False,
            reviewed_by_human=False
        )
        
        # Simular que a passage foi nula no BD (limpar se resolveu no save)
        dev.passage = None
        DevotionalContent.objects.filter(id=dev.id).update(passage=None)
        
        # Verificar que de fato ficou orfão
        dev.refresh_from_db()
        self.assertIsNone(dev.passage)
        
        # 2. Chamar o comando de backfill
        call_command('backfill_devotional_passages')
        
        # 3. Validar que foi resolvido e vinculado retroativamente
        dev.refresh_from_db()
        self.assertIsNotNone(dev.passage)
        self.assertEqual(dev.passage.canonical_id, "PSA.34.18")

    def test_canonical_id_standard_dots(self):
        dev = DevotionalContent.objects.create(
            emotion=self.emotion,
            title="Padronização de Pontos",
            scripture_reference="Salmos 34:18",
            scripture_text="O Senhor está perto...",
            reflection="O Senhor está perto.",
            prayer="Amém.",
            share_quote="O Senhor está perto.",
            is_active=True,
            reviewed_by_human=True
        )
        self.assertEqual(dev.passage.canonical_id, "PSA.34.18")
        self.assertNotIn(":", dev.passage.canonical_id)

    def test_update_fields_persists_resolved_passage(self):
        dev = DevotionalContent.objects.create(
            emotion=self.emotion,
            title="Devocional Orfao Corrigido",
            scripture_reference="Romanos 8:28",
            scripture_text="Todas as coisas cooperam para o bem.",
            reflection="Deus trabalha tambem no que nao conseguimos ver.",
            prayer="Senhor, firma meu coracao na tua providencia.",
            share_quote="Deus tece o bem no invisivel.",
            is_active=False,
            reviewed_by_human=False
        )
        DevotionalContent.objects.filter(id=dev.id).update(passage=None)

        dev.refresh_from_db()
        self.assertIsNone(dev.passage_id)

        dev.share_quote = "Deus tece o bem no invisivel."
        dev.save(update_fields=['share_quote'])

        dev.refresh_from_db()
        self.assertIsNotNone(dev.passage_id)
        self.assertEqual(dev.passage.canonical_id, "ROM.8.28")

    def test_save_active_without_passage_fails(self):
        from django.core.exceptions import ValidationError

        dev = DevotionalContent(
            emotion=self.emotion,
            title="Ativo sem passagem",
            scripture_reference="",
            scripture_text="",
            reflection="Texto",
            prayer="Oracao",
            share_quote="Frase",
            is_active=True,
            reviewed_by_human=False
        )

        with self.assertRaises(ValidationError):
            dev.save()


