from django.test import TestCase
from django.urls import reverse
from .models import DevotionalContent, Emotion

class DevotionalFieldsAPITest(TestCase):
    def setUp(self):
        self.emotion = Emotion.objects.create(name="Ansioso", slug="ansioso")
        self.devotional = DevotionalContent.objects.create(
            emotion=self.emotion,
            title="Test Devotional",
            scripture_reference="Salmo 1",
            scripture_text="Bem-aventurado o homem...",
            reflection="Reflection test",
            anchor_text="Anchor text test",
            carry_with_you_text="Carry text test",
            word_continues_text="Continues text test",
            prayer="Prayer test",
            share_quote="Share quote test",
            is_active=True,
            reviewed_by_human=True
        )

    def test_api_returns_all_editorial_fields(self):
        from .serializers import DevotionalContentSerializer
        
        serializer = DevotionalContentSerializer(self.devotional)
        data = serializer.data
        
        self.assertIn('reflection', data)
        self.assertIn('anchor_text', data)
        self.assertIn('carry_with_you_text', data)
        self.assertIn('word_continues_text', data)
        self.assertIn('prayer', data)
        self.assertIn('share_quote', data)
        
        self.assertEqual(data['anchor_text'], "Anchor text test")
        self.assertEqual(data['carry_with_you_text'], "Carry text test")
        self.assertEqual(data['word_continues_text'], "Continues text test")
