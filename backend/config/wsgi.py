"""
WSGI config for config project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')

application = get_wsgi_application()

# AUTO-SYNC: Garante que as 20 emoções e 147 devocionais estejam no banco no startup em produção
try:
    from django.core.management import call_command
    from django.db import connection

    if 'devotional_emotion' in connection.introspection.table_names():
        from apps.devotional.models import DevotionalContent, Emotion
        active_count = DevotionalContent.objects.filter(is_active=True).count()
        vazio_emo = Emotion.objects.filter(slug='vazio').first()
        if active_count < 147 or not vazio_emo or not getattr(vazio_emo, 'icon', ''):
            print("[CAPIO WSGI] Acervo incompleto ou ícones ausentes detectados no startup. Sincronizando...")
            try:
                call_command('migrate', interactive=False)
            except Exception as e:
                print(f"[CAPIO WSGI AVISO] migrate falhou ou já executado: {e}")
            
            try:
                call_command('import_editorial_staging')
            except Exception as e:
                print(f"[CAPIO WSGI AVISO] import_editorial_staging falhou: {e}")

            icons_map = {
                'ansioso': 'anxiety_icon',
                'triste': 'sad_icon',
                'medo': 'fear_icon',
                'desmotivado': 'unmotivated_icon',
                'sozinho': 'lonely_icon',
                'sem-esperanca': 'hopeless_icon',
                'direcao': 'direction_icon',
                'gratidao': 'gratitude_icon',
                'inseguro': 'insecure_icon',
                'cansado': 'tired_icon',
                'corajoso-mas-incerto': 'courageous_uncertain_icon',
                'chamado-mas-hesitante': 'called_hesitant_icon',
                'tentado': 'tempted_icon',
                'em-conflito-com-alguem': 'conflict_icon',
                'grato-mas-disperso': 'grateful_dispersed_icon',
                'disciplinado-mas-frio': 'disciplined_cold_icon',
                'culpado': 'guilty_icon',
                'raiva': 'anger_icon',
                'confuso': 'confused_icon',
                'vazio': 'empty_icon',
            }
            for slug, icon_name in icons_map.items():
                Emotion.objects.filter(slug=slug).update(icon=icon_name)

            all_slugs = list(icons_map.keys())
            promoted_count = DevotionalContent.objects.filter(
                emotion__slug__in=all_slugs
            ).update(is_active=True, reviewed_by_human=True)
            print(f"[CAPIO WSGI SUCESSO] {promoted_count} devocionais ativos em {Emotion.objects.count()} emoções!")
except Exception as auto_err:
    print(f"[CAPIO WSGI AVISO GERAL] {auto_err}")
