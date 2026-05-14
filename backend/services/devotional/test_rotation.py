from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.devotional.models import Emotion, DevotionalContent, UserDevotional
from apps.ai_core.models import GeneratedResponse
from services.devotional.devotional_service import DevotionalService

User = get_user_model()

class DevotionalRotationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='rotation_user', password='pw')
        self.emotion = Emotion.objects.create(name='Alegria', slug='alegria')
        
        # Criando 3 conteúdos de Alegria
        self.c1 = DevotionalContent.objects.create(
            emotion=self.emotion, title='Alegria 1', scripture_text='T1', reflection='R1', prayer='P1'
        )
        self.c2 = DevotionalContent.objects.create(
            emotion=self.emotion, title='Alegria 2', scripture_text='T2', reflection='R2', prayer='P2'
        )
        self.c3 = DevotionalContent.objects.create(
            emotion=self.emotion, title='Alegria 3', scripture_text='T3', reflection='R3', prayer='P3'
        )

    def test_different_content_received(self):
        # Usuário acessa 1 vez (não sabemos qual vai vir, pois o primeiro mock pode vir via AI ou um aleatório se já tivessem)
        # Como tem conteúdos, vai pegar aleatoriamente c1, c2 ou c3
        res1 = DevotionalService.get_for_emotion('alegria', self.user)
        self.assertTrue(res1['cached'])
        
        # Ao chamar novamente, não deve vir o mesmo
        res2 = DevotionalService.get_for_emotion('alegria', self.user)
        self.assertNotEqual(res1['title'], res2['title'])

    def test_exclude_last_seen_and_metadata(self):
        # Limpar views
        UserDevotional.objects.all().delete()
        
        res1 = DevotionalService.get_for_emotion('alegria', self.user)
        res2 = DevotionalService.get_for_emotion('alegria', self.user)
        
        # Verificar metadados do último GeneratedResponse
        last_response = GeneratedResponse.objects.order_by('-created_at').first()
        self.assertTrue(last_response.metadata.get('rotation'))
        self.assertEqual(last_response.metadata.get('rotation_strategy'), 'exclude_recent')

    def test_fallback_reusing_oldest(self):
        UserDevotional.objects.all().delete()
        
        # Acessa os 3 conteúdos disponíveis
        r1 = DevotionalService.get_for_emotion('alegria', self.user)
        r2 = DevotionalService.get_for_emotion('alegria', self.user)
        r3 = DevotionalService.get_for_emotion('alegria', self.user)
        
        titles_seen = {r1['title'], r2['title'], r3['title']}
        self.assertEqual(len(titles_seen), 3) # Viu todos diferentes
        
        # Agora todos estão no histórico recente.
        # O oldest visto é r1, então o próximo deve ser r1['title']
        r4 = DevotionalService.get_for_emotion('alegria', self.user)
        self.assertEqual(r4['title'], r1['title'])
        
        # Verificar metadados do fallback
        last_response = GeneratedResponse.objects.order_by('-created_at').first()
        self.assertTrue(last_response.metadata.get('rotation'))
        self.assertEqual(last_response.metadata.get('rotation_strategy'), 'exclude_recent')
