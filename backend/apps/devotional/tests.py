from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from unittest.mock import patch, MagicMock
from apps.devotional.models import Emotion, DevotionalContent, UserDevotional

User = get_user_model()

EDITORIAL_URL = '/api/devotional/editorial/generate/'

def _make_ai_response(scripture_reference, emotional_theme='Cuidado de Deus'):
    return {
        "title": f"Devocional sobre {emotional_theme}",
        "scripture_reference": scripture_reference,
        "scripture_text": "Texto bíblico de exemplo.",
        "reflection": "Reflexão de exemplo.",
        "prayer": "Oração de exemplo.",
        "share_quote": "Frase de exemplo.",
        "emotional_theme": emotional_theme,
        "ai_generated": True,
    }

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


class EditorialDeduplicationTests(APITestCase):
    """Testes de diversidade editorial e proteção contra passagens duplicadas."""

    def setUp(self):
        self.user = User.objects.create_user(username='editoruser', password='editorpassword')
        self.user.is_staff = True
        self.user.save()
        self.client.force_authenticate(user=self.user)
        self.emotion = Emotion.objects.create(name="Ansioso", slug="ansioso")

    def _create_devotional(self, title, scripture_reference, emotional_theme='Espera silenciosa'):
        return DevotionalContent.objects.create(
            emotion=self.emotion,
            title=title,
            scripture_reference=scripture_reference,
            scripture_text="Texto bíblico.",
            reflection="Reflexão.",
            prayer="Oração.",
            share_quote="Frase.",
            emotional_theme=emotional_theme,
            is_active=True,
            reviewed_by_human=True,
        )

    def test_editorial_generate_sends_excluded_passages_to_ai(self):
        """View deve consultar o banco e passar excluded_passages para a IA antes de gerar."""
        self._create_devotional("Devocional A", "Salmos 23:1-3", "Repouso no pastor")
        self._create_devotional("Devocional B", "Filipenses 4:6-7", "Entrega na oração")

        with patch('apps.devotional.views.get_ai_service') as mock_get_ai:
            mock_ai = MagicMock()
            mock_ai.editorial_generate_devotional.return_value = _make_ai_response("1 Pedro 5:7", "Cuidado de Deus")
            mock_get_ai.return_value = mock_ai

            response = self.client.post(EDITORIAL_URL, {'emotion_slug': 'ansioso'}, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        call_kwargs = mock_ai.editorial_generate_devotional.call_args
        excluded_passages = call_kwargs.kwargs.get('excluded_passages', [])
        self.assertIn("Salmos 23:1-3", excluded_passages)
        self.assertIn("Filipenses 4:6-7", excluded_passages)

    def test_editorial_generate_sends_excluded_themes_to_ai(self):
        """View deve passar excluded_themes para a IA com os temas emocionais já existentes."""
        self._create_devotional("Devocional A", "Salmos 23:1-3", "A quietude na espera")
        self._create_devotional("Devocional B", "Filipenses 4:6-7", "O repouso silencioso")

        with patch('apps.devotional.views.get_ai_service') as mock_get_ai:
            mock_ai = MagicMock()
            mock_ai.editorial_generate_devotional.return_value = _make_ai_response("1 Pedro 5:7", "Cuidado de Deus")
            mock_get_ai.return_value = mock_ai

            self.client.post(EDITORIAL_URL, {'emotion_slug': 'ansioso'}, format='json')

        call_kwargs = mock_ai.editorial_generate_devotional.call_args
        excluded_themes = call_kwargs.kwargs.get('excluded_themes', [])
        self.assertIn("A quietude na espera", excluded_themes)
        self.assertIn("O repouso silencioso", excluded_themes)

    def test_editorial_generate_sends_excluded_titles_to_ai(self):
        """View deve passar excluded_titles para a IA com os títulos já existentes."""
        self._create_devotional("O Repouso na Espera", "Salmos 23:1-3")
        self._create_devotional("A Espera no Silêncio", "Filipenses 4:6-7")

        with patch('apps.devotional.views.get_ai_service') as mock_get_ai:
            mock_ai = MagicMock()
            mock_ai.editorial_generate_devotional.return_value = _make_ai_response("1 Pedro 5:7")
            mock_get_ai.return_value = mock_ai

            self.client.post(EDITORIAL_URL, {'emotion_slug': 'ansioso'}, format='json')

        call_kwargs = mock_ai.editorial_generate_devotional.call_args
        excluded_titles = call_kwargs.kwargs.get('excluded_titles', [])
        self.assertIn("O Repouso na Espera", excluded_titles)
        self.assertIn("A Espera no Silêncio", excluded_titles)

    def test_editorial_generate_no_exclusions_for_empty_library(self):
        """Sem devocionais existentes, IA é chamada com listas de exclusão vazias."""
        with patch('apps.devotional.views.get_ai_service') as mock_get_ai:
            mock_ai = MagicMock()
            mock_ai.editorial_generate_devotional.return_value = _make_ai_response("Mateus 6:34")
            mock_get_ai.return_value = mock_ai

            response = self.client.post(EDITORIAL_URL, {'emotion_slug': 'ansioso'}, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        call_kwargs = mock_ai.editorial_generate_devotional.call_args
        self.assertEqual(call_kwargs.kwargs.get('excluded_passages', []), [])
        self.assertEqual(call_kwargs.kwargs.get('excluded_themes', []), [])
        self.assertEqual(call_kwargs.kwargs.get('excluded_titles', []), [])

    def test_editorial_generate_rejects_duplicate_on_persistent_collision(self):
        """IA retorna mesma passagem nas duas tentativas: deve retornar 409 com erro claro."""
        # "Salmos 23:1-3" normaliza para PSA.23.1-3
        self._create_devotional("Devocional com Salmos 23", "Salmos 23:1-3")

        with patch('apps.devotional.views.get_ai_service') as mock_get_ai:
            mock_ai = MagicMock()
            # Ambas as tentativas retornam a mesma passagem duplicada
            mock_ai.editorial_generate_devotional.return_value = _make_ai_response("Salmos 23:1-3", "Repouso duplicado")
            mock_get_ai.return_value = mock_ai

            response = self.client.post(EDITORIAL_URL, {'emotion_slug': 'ansioso'}, format='json')

        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(response.data['error'], 'duplicate_passage')
        self.assertIn("direção espiritual mais específica", response.data['message'])
        # IA deve ter sido chamada exatamente 2 vezes (tentativa original + retry)
        self.assertEqual(mock_ai.editorial_generate_devotional.call_count, 2)

    def test_editorial_generate_succeeds_on_retry_with_unique_passage(self):
        """Primeira tentativa duplicada, segunda tentativa com passagem única: deve retornar 200."""
        self._create_devotional("Devocional com Salmos 23", "Salmos 23:1-3")

        with patch('apps.devotional.views.get_ai_service') as mock_get_ai:
            mock_ai = MagicMock()
            mock_ai.editorial_generate_devotional.side_effect = [
                _make_ai_response("Salmos 23:1-3", "Duplicado"),      # 1ª tentativa: duplicada
                _make_ai_response("1 Pedro 5:7", "Cuidado de Deus"),  # 2ª tentativa: única
            ]
            mock_get_ai.return_value = mock_ai

            response = self.client.post(EDITORIAL_URL, {'emotion_slug': 'ansioso'}, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['scripture_reference'], "1 Pedro 5:7")
        self.assertEqual(mock_ai.editorial_generate_devotional.call_count, 2)

    def test_editorial_generate_retry_receives_reinforced_direction(self):
        """No retry, a direção enviada à IA deve mencionar a passagem duplicada detectada."""
        self._create_devotional("Devocional com Salmos 23", "Salmos 23:1-3")

        with patch('apps.devotional.views.get_ai_service') as mock_get_ai:
            mock_ai = MagicMock()
            mock_ai.editorial_generate_devotional.side_effect = [
                _make_ai_response("Salmos 23:1-3"),
                _make_ai_response("1 Pedro 5:7"),
            ]
            mock_get_ai.return_value = mock_ai

            self.client.post(EDITORIAL_URL, {'emotion_slug': 'ansioso'}, format='json')

        # Verificar que a segunda chamada recebeu um tone_or_direction reforçado
        second_call_kwargs = mock_ai.editorial_generate_devotional.call_args_list[1].kwargs
        retry_direction = second_call_kwargs.get('tone_or_direction', '')
        self.assertIn("Salmos 23:1-3", retry_direction)
        self.assertIn("JÁ EXISTE", retry_direction)

    def test_editorial_generate_unique_passages_are_accepted_without_retry(self):
        """Passagem única retornada pela IA não deve disparar retry (IA chamada apenas uma vez)."""
        self._create_devotional("Devocional existente", "Salmos 23:1-3")

        with patch('apps.devotional.views.get_ai_service') as mock_get_ai:
            mock_ai = MagicMock()
            mock_ai.editorial_generate_devotional.return_value = _make_ai_response("Mateus 6:25-27", "Entrega do amanhã")
            mock_get_ai.return_value = mock_ai

            response = self.client.post(EDITORIAL_URL, {'emotion_slug': 'ansioso'}, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(mock_ai.editorial_generate_devotional.call_count, 1)

    def test_editorial_generate_tone_direction_preserved_on_retry(self):
        """Direção espiritual original do admin deve ser preservada no retry, além do aviso de duplicidade."""
        self._create_devotional("Devocional com Salmos 23", "Salmos 23:1-3")

        with patch('apps.devotional.views.get_ai_service') as mock_get_ai:
            mock_ai = MagicMock()
            mock_ai.editorial_generate_devotional.side_effect = [
                _make_ai_response("Salmos 23:1-3"),
                _make_ai_response("1 Pedro 5:7"),
            ]
            mock_get_ai.return_value = mock_ai

            self.client.post(
                EDITORIAL_URL,
                {'emotion_slug': 'ansioso', 'tone_or_direction': 'ansiedade antes de dormir'},
                format='json',
            )

        second_call_kwargs = mock_ai.editorial_generate_devotional.call_args_list[1].kwargs
        retry_direction = second_call_kwargs.get('tone_or_direction', '')
        self.assertIn("ansiedade antes de dormir", retry_direction)
        self.assertIn("JÁ EXISTE", retry_direction)

    def test_editorial_generate_sends_semantic_cooldown_when_words_saturated(self):
        """Palavras da watchlist presentes em 2+ devocionais recentes devem ser passadas no semantic_cooldown_words."""
        # Criar 3 devocionais com "silêncio" e "repouso" no conteúdo (saturam watchlist)
        self._create_devotional(
            "O silêncio na espera", "Salmos 23:1-3",
            emotional_theme="Repouso no silêncio"
        )
        DevotionalContent.objects.filter(title="O silêncio na espera").update(
            reflection="Há um silêncio que acolhe a alma em repouso."
        )
        self._create_devotional(
            "Quando o repouso chega", "Filipenses 4:6-7",
            emotional_theme="Silêncio na entrega"
        )
        DevotionalContent.objects.filter(title="Quando o repouso chega").update(
            reflection="O repouso chega quando paramos de resistir ao silêncio."
        )

        with patch('apps.devotional.views.get_ai_service') as mock_get_ai:
            mock_ai = MagicMock()
            mock_ai.editorial_generate_devotional.return_value = _make_ai_response("Mateus 6:25", "Entrega do amanhã")
            mock_get_ai.return_value = mock_ai

            response = self.client.post(EDITORIAL_URL, {'emotion_slug': 'ansioso'}, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        call_kwargs = mock_ai.editorial_generate_devotional.call_args.kwargs
        cooldown_words = call_kwargs.get('semantic_cooldown_words', [])
        # "silêncio" e "repouso" aparecem em 2+ devocionais — devem estar no cooldown
        self.assertIn('silêncio', cooldown_words)
        self.assertIn('repouso', cooldown_words)

    def test_editorial_generate_no_semantic_cooldown_for_empty_library(self):
        """Sem devocionais existentes, semantic_cooldown_words deve ser lista vazia."""
        with patch('apps.devotional.views.get_ai_service') as mock_get_ai:
            mock_ai = MagicMock()
            mock_ai.editorial_generate_devotional.return_value = _make_ai_response("Mateus 6:34")
            mock_get_ai.return_value = mock_ai

            response = self.client.post(EDITORIAL_URL, {'emotion_slug': 'ansioso'}, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        call_kwargs = mock_ai.editorial_generate_devotional.call_args.kwargs
        self.assertEqual(call_kwargs.get('semantic_cooldown_words', []), [])

    def test_editorial_generate_semantic_cooldown_excludes_rare_words(self):
        """Palavra da watchlist que aparece em apenas 1 devocional NÃO deve entrar no cooldown."""
        self._create_devotional(
            "O mistério da fé", "João 14:27",
            emotional_theme="Paz que transcende"
        )
        DevotionalContent.objects.filter(title="O mistério da fé").update(
            reflection="Há um mistério na paz que a razão não alcança."
        )

        with patch('apps.devotional.views.get_ai_service') as mock_get_ai:
            mock_ai = MagicMock()
            mock_ai.editorial_generate_devotional.return_value = _make_ai_response("Romanos 8:28")
            mock_get_ai.return_value = mock_ai

            self.client.post(EDITORIAL_URL, {'emotion_slug': 'ansioso'}, format='json')

        call_kwargs = mock_ai.editorial_generate_devotional.call_args.kwargs
        cooldown_words = call_kwargs.get('semantic_cooldown_words', [])
        # "mistério" aparece em apenas 1 devocional — não deve entrar no cooldown
        self.assertNotIn('mistério', cooldown_words)


class NewEmotionsTests(APITestCase):
    """Testes de integridade e cobertura para as novas 6 emoções e estados espirituais (Fase 3)."""

    def setUp(self):
        self.user = User.objects.create_user(username='staffuser', password='staffpassword')
        self.user.is_staff = True
        self.user.save()
        self.client.force_authenticate(user=self.user)
        
        # Cria as 6 novas emoções no banco de dados se não existirem
        self.new_slugs = [
            "corajoso-mas-incerto",
            "chamado-mas-hesitante",
            "tentado",
            "em-conflito-com-alguem",
            "grato-mas-disperso",
            "disciplinado-mas-frio"
        ]
        self.new_emotions = []
        for slug in self.new_slugs:
            name = slug.replace("-", " ").capitalize()
            emo, _ = Emotion.objects.get_or_create(slug=slug, defaults={"name": name})
            self.new_emotions.append(emo)
            
        # Cria a antiga para garantir que coexistem
        self.old_emotion, _ = Emotion.objects.get_or_create(slug="ansioso", defaults={"name": "Ansioso"})

    def test_new_emotions_endpoints_accepts_and_serves(self):
        """Valida que o endpoint /api/devotional/by-emotion/ aceita e serve as novas emoções sem quebras."""
        url = '/api/devotional/by-emotion/'
        
        for slug in self.new_slugs:
            # Criamos um devocional ativo e revisado para o teste simples (sem chamar IA)
            emo = Emotion.objects.get(slug=slug)
            DevotionalContent.objects.create(
                emotion=emo,
                title=f"Devocional para {slug}",
                scripture_reference="Josué 1:9" if slug == "corajoso-mas-incerto" else "Salmo 23",
                scripture_text="Texto da Palavra",
                reflection="Reflexão monástica.",
                prayer="Oração profunda.",
                share_quote="Citação de fé.",
                is_active=True,
                reviewed_by_human=True
            )
            
            data = {'emotion_slug': slug}
            response = self.client.post(url, data, format='json')
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data['title'], f"Devocional para {slug}")
            self.assertFalse(response.data['ai_generated'])

    def test_new_emotions_generation_integration(self):
        """Valida que o gerador de devocionais (via mock/IA) opera adequadamente para os novos estados ativados."""
        from services.ai.anthropic import AnthropicAIService
        from services.devotional.devotional_service import EMOTION_SCRIPTURES
        service = AnthropicAIService()
        
        # Testar para cada uma das novas emoções que o mapeamento de passagens e ângulos existe no service
        for slug in self.new_slugs:
            # No devotional_service, o pool EMOTION_SCRIPTURES usa chaves com underlines
            underscore_key = slug.replace("-", "_")
            self.assertIn(underscore_key, EMOTION_SCRIPTURES)
            self.assertTrue(len(EMOTION_SCRIPTURES[underscore_key]) > 0)
            
            # No anthropic, o serviço de IA usa chaves normalizadas com hifens (slug)
            self.assertIn(slug, service._EDITORIAL_PRIMARY_SCRIPTURES)
            self.assertTrue(len(service._EDITORIAL_PRIMARY_SCRIPTURES[slug]) > 0)
            
            # Valida ângulos humanos configurados no anthropic
            self.assertIn(slug, service._EDITORIAL_EMOTION_ANGLES)
            self.assertTrue(len(service._EDITORIAL_EMOTION_ANGLES[slug]) > 0)
            
    def test_old_emotions_continue_working_harmoniously(self):
        """Garante que as emoções antigas e o seu fluxo original continuam funcionando sem qualquer interferência."""
        # Criamos devocional para a antiga
        DevotionalContent.objects.create(
            emotion=self.old_emotion,
            title="Antiga quietude",
            scripture_reference="Salmos 23",
            scripture_text="O Senhor é o meu pastor",
            reflection="Reflexão antiga.",
            prayer="Oração antiga.",
            share_quote="Pastor eterno.",
            is_active=True,
            reviewed_by_human=True
        )
        
        url = '/api/devotional/by-emotion/'
        data = {'emotion_slug': 'ansioso'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], "Antiga quietude")


