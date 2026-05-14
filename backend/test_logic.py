import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from services.ai import get_ai_service
from services.filters.content_filter import ContentFilter, FilterAction, get_fallback_for_hard_block

def run_tests():
    print("=== TESTANDO MOCK AI SERVICE ===")
    ai_service = get_ai_service()
    
    print("\n1. Explain Passage (João 3:16):")
    res1 = ai_service.explain_passage("jo 3:16", "João 3:16")
    print(res1)
    
    print("\n2. Devotional for Emotion (Ansioso):")
    res2 = ai_service.devotional_for_emotion("Ansioso")
    print(res2['title'], "-", res2['scripture_reference'])
    
    print("\n3. Devotional for Emotion (Desconhecida - fallback para Ansioso ou genérico):")
    res3 = ai_service.devotional_for_emotion("Inexistente")
    print(res3['title'], "-", res3['scripture_reference'])
    
    print("\n4. Generate Reflection (2023-10-10):")
    res4 = ai_service.generate_reflection("2023-10-10")
    print(res4['title'], "-", res4['scripture_reference'])

    print("\n=== TESTANDO CONTENT FILTER ===")
    
    print("\n1. Teste CLEAN (oração comum):")
    clean_text = "Gostaria de uma oração para me dar forças hoje."
    res_clean = ContentFilter.check_input(clean_text)
    print(f"Texto: '{clean_text}' -> Resultado: {res_clean}")

    print("\n2. Teste SOFT_FLAG (dúvida de fé / termo sensível):")
    soft_text = "Deus me abandonou, não consigo rezar mais."
    res_soft = ContentFilter.check_input(soft_text)
    print(f"Texto: '{soft_text}' -> Resultado: {res_soft}")
    
    print("\n3. Teste HARD_BLOCK (termo proibido):")
    hard_text = "Quero fazer um pacto e usar tarot para ver meu futuro."
    res_hard = ContentFilter.check_input(hard_text)
    print(f"Texto: '{hard_text}' -> Resultado: {res_hard}")
    print(f"Fallback Estático: {get_fallback_for_hard_block()}")

if __name__ == '__main__':
    run_tests()
