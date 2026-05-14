from django.test import TestCase
from django.core.management import call_command
from apps.devotional.models import DevotionalContent, Emotion

class SeedInitialDataTests(TestCase):
    def test_seed_creates_ansioso_devotionals(self):
        # Garante que começa limpo
        self.assertEqual(DevotionalContent.objects.count(), 0)

        # Roda o seed
        call_command('seed_initial_data')

        # Verifica se Emotion ansioso existe
        emotion = Emotion.objects.get(slug='ansioso')
        self.assertIsNotNone(emotion)

        # Verifica se criou os 10 devocionais
        devotionals = DevotionalContent.objects.filter(emotion=emotion)
        self.assertEqual(devotionals.count(), 10)

        # Verifica se os campos is_active e ai_generated estão corretos
        for dev in devotionals:
            self.assertTrue(dev.is_active)
            self.assertFalse(dev.ai_generated)

    def test_seed_creates_triste_devotionals(self):
        # Garante que começa limpo
        self.assertEqual(DevotionalContent.objects.count(), 0)

        # Roda o seed
        call_command('seed_initial_data')

        # Verifica se Emotion triste existe
        emotion = Emotion.objects.get(slug='triste')
        self.assertIsNotNone(emotion)

        # Verifica se criou os 10 devocionais
        devotionals = DevotionalContent.objects.filter(emotion=emotion)
        self.assertEqual(devotionals.count(), 10)

        # Verifica se os campos is_active e ai_generated estão corretos
        for dev in devotionals:
            self.assertTrue(dev.is_active)
            self.assertFalse(dev.ai_generated)

    def test_seed_creates_medo_devotionals(self):
        # Garante que começa limpo
        self.assertEqual(DevotionalContent.objects.count(), 0)

        # Roda o seed
        call_command('seed_initial_data')

        # Verifica se Emotion medo existe
        emotion = Emotion.objects.get(slug='medo')
        self.assertIsNotNone(emotion)

        # Verifica se criou os 8 devocionais
        devotionals = DevotionalContent.objects.filter(emotion=emotion)
        self.assertEqual(devotionals.count(), 8)

        # Verifica se os campos is_active e ai_generated estão corretos
        for dev in devotionals:
            self.assertTrue(dev.is_active)
            self.assertFalse(dev.ai_generated)

    def test_seed_creates_desmotivado_devotionals(self):
        # Garante que começa limpo
        self.assertEqual(DevotionalContent.objects.count(), 0)

        # Roda o seed
        call_command('seed_initial_data')

        # Verifica se Emotion desmotivado existe
        emotion = Emotion.objects.get(slug='desmotivado')
        self.assertIsNotNone(emotion)

        # Verifica se criou os 8 devocionais
        devotionals = DevotionalContent.objects.filter(emotion=emotion)
        self.assertEqual(devotionals.count(), 8)

        # Verifica se os campos is_active e ai_generated estão corretos
        for dev in devotionals:
            self.assertTrue(dev.is_active)
            self.assertFalse(dev.ai_generated)

    def test_seed_creates_sozinho_devotionals(self):
        # Garante que começa limpo
        self.assertEqual(DevotionalContent.objects.count(), 0)

        # Roda o seed
        call_command('seed_initial_data')

        # Verifica se Emotion sozinho existe
        emotion = Emotion.objects.get(slug='sozinho')
        self.assertIsNotNone(emotion)

        # Verifica se criou os 8 devocionais
        devotionals = DevotionalContent.objects.filter(emotion=emotion)
        self.assertEqual(devotionals.count(), 8)

        # Verifica se os campos is_active e ai_generated estão corretos
        for dev in devotionals:
            self.assertTrue(dev.is_active)
            self.assertFalse(dev.ai_generated)

    def test_seed_creates_sem_esperanca_devotionals(self):
        # Garante que começa limpo
        self.assertEqual(DevotionalContent.objects.count(), 0)

        # Roda o seed
        call_command('seed_initial_data')

        # Verifica se Emotion sem_esperanca existe
        emotion = Emotion.objects.get(slug='sem-esperanca')
        self.assertIsNotNone(emotion)

        # Verifica se criou os 8 devocionais
        devotionals = DevotionalContent.objects.filter(emotion=emotion)
        self.assertEqual(devotionals.count(), 8)

        # Verifica se os campos is_active e ai_generated estão corretos
        for dev in devotionals:
            self.assertTrue(dev.is_active)
            self.assertFalse(dev.ai_generated)

    def test_seed_creates_direcao_devotionals(self):
        # Garante que começa limpo
        self.assertEqual(DevotionalContent.objects.count(), 0)

        # Roda o seed
        call_command('seed_initial_data')

        # Verifica se Emotion direcao existe
        emotion = Emotion.objects.get(slug='direcao')
        self.assertIsNotNone(emotion)

        # Verifica se criou os 8 devocionais
        devotionals = DevotionalContent.objects.filter(emotion=emotion)
        self.assertEqual(devotionals.count(), 8)

        # Verifica se os campos is_active e ai_generated estão corretos
        for dev in devotionals:
            self.assertTrue(dev.is_active)
            self.assertFalse(dev.ai_generated)

    def test_seed_creates_gratidao_devotionals(self):
        # Garante que começa limpo
        self.assertEqual(DevotionalContent.objects.count(), 0)

        # Roda o seed
        call_command('seed_initial_data')

        # Verifica se Emotion gratidao existe
        emotion = Emotion.objects.get(slug='gratidao')
        self.assertIsNotNone(emotion)

        # Verifica se criou os 8 devocionais
        devotionals = DevotionalContent.objects.filter(emotion=emotion)
        self.assertEqual(devotionals.count(), 8)

        # Verifica se os campos is_active e ai_generated estão corretos
        for dev in devotionals:
            self.assertTrue(dev.is_active)
            self.assertFalse(dev.ai_generated)

    def test_seed_is_idempotent(self):
        # Roda uma vez
        call_command('seed_initial_data')
        count_first = DevotionalContent.objects.count()

        # Roda de novo
        call_command('seed_initial_data')
        count_second = DevotionalContent.objects.count()

        # O count deve ser exatamente igual, não deve duplicar
        self.assertEqual(count_first, count_second)
