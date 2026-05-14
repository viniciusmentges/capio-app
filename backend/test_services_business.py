import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.users.models import User
from services.bible.explanation_service import BibleService
from services.devotional.devotional_service import DevotionalService
from services.reflection.reflection_service import ReflectionService
from services.feedback.feedback_service import FeedbackService
from services.exceptions import ContentBlockedException

def run_tests():
    # Cria um usuário de teste se não existir
    user, _ = User.objects.get_or_create(username='test_user_services')

    print("=== TESTANDO BIBLE SERVICE ===")
    try:
        res_bible = BibleService.explain("João 3:16", user)
        print("Bible [1º acesso]:", res_bible['reference_display'], "| Cached:", res_bible['cached'])
        res_bible_cached = BibleService.explain("jo 3:16", user)
        print("Bible [2º acesso]:", res_bible_cached['reference_display'], "| Cached:", res_bible_cached['cached'])
    except ContentBlockedException as e:
        print("Bloqueado:", str(e))

    print("\n=== TESTANDO DEVOTIONAL SERVICE ===")
    res_devo = DevotionalService.get_for_emotion("ansioso", user)
    print("Devotional [Ansioso]:", res_devo['title'], "| Cached:", res_devo['cached'])
    
    print("\n=== TESTANDO REFLECTION SERVICE ===")
    res_refl = ReflectionService.get_today(user)
    print("Reflection [Hoje]:", res_refl['reflection']['title'])
    
    # Testando o save_response
    print("\n=== TESTANDO SAVE RESPONSE (REFLECTION) ===")
    ReflectionService.save_response(user, res_refl['reflection']['id'], "Foi muito tocante.")
    res_refl_after = ReflectionService.get_today(user)
    print("Resposta salva no banco:", res_refl_after['user_response'])

    print("\n=== TESTANDO FEEDBACK SERVICE ===")
    res_feedback = FeedbackService.submit(
        user=user,
        response_type='BIBLE',
        content_ref_id=1,  # A primeira explicação salva
        helpful=True,
        comment="Muito inspirador!"
    )
    print("Feedback salvo:", res_feedback)

if __name__ == '__main__':
    run_tests()
