from django.core.management.base import BaseCommand
from services.devotional.devotional_service import DevotionalService
from django.contrib.auth import get_user_model
import json

class Command(BaseCommand):
    def handle(self, *args, **options):
        User = get_user_model()
        user = User.objects.first()
        res = DevotionalService.get_for_emotion('ansioso', user)
        print(json.dumps({
            'anchor_text': res.get('anchor_text'),
            'carry_with_you_text': res.get('carry_with_you_text'),
            'word_continues_text': res.get('word_continues_text')
        }, indent=2, ensure_ascii=False))
