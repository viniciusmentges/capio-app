import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.devotional.models import Emotion

ordered_slugs = [
    "ansioso",
    "em-paz",
    "triste",
    "esperancoso",
    "medo",
    "confiante",
    "desmotivado",
    "animado",
    "sozinho",
    "amado",
    "sem-esperanca",
    "feliz",
    "direcao",
    "inspirado",
    "gratidao",
    "realizado",
    "corajoso-mas-incerto",
    "pronto-para-servir",
    "chamado-mas-hesitante",
    "encantado",
    "tentado",
    "em-conflito-com-alguem",
    "grato-mas-disperso",
    "disciplinado-mas-frio",
    "inseguro",
    "cansado",
    "culpado",
    "envergonhado",
    "raiva",
    "confuso",
    "vazio"
]

missing = []

for idx, slug in enumerate(ordered_slugs, start=1):
    emotion = Emotion.objects.filter(slug=slug).first()
    if emotion:
        emotion.display_order = idx
        emotion.save(update_fields=['display_order'])
        print(f"[{idx}] {slug} -> OK")
    else:
        print(f"[{idx}] {slug} -> NAO ENCONTRADO (Normal se a importacao ainda nao rodou)")
        missing.append(slug)
