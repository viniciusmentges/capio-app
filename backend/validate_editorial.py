"""
Validação qualitativa editorial CAPIO — 5 gerações consecutivas por emoção.
Cada resultado é salvo no banco (rascunho) antes da próxima geração,
garantindo que exclusions, blacklist e semantic cooldown acumulem corretamente.

Executar com:
    .venv/Scripts/python.exe validate_editorial.py
"""
import os
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.devotional.models import Emotion, DevotionalContent
from apps.devotional.views import EditorialDevotionalGenerateView
from services.ai import get_ai_service

GENERATIONS_PER_EMOTION = 5
EMOTIONS_TO_TEST = [
    ('ansioso',         'Ansioso'),
    ('medo',            'Medo'),
    ('desesperancoso',  'Desesperancoso'),
]


def build_exclusion_lists(emotion):
    existing_data = DevotionalContent.objects.filter(
        emotion=emotion
    ).select_related('passage').values_list(
        'scripture_reference', 'passage__canonical_id', 'title', 'emotional_theme'
    )
    excluded_passages, excluded_canonical_ids, excluded_themes, excluded_titles = [], set(), [], []
    for ref, canonical_id, title, theme in existing_data:
        if ref and ref not in excluded_passages:
            excluded_passages.append(ref)
        if canonical_id and canonical_id not in excluded_canonical_ids:
            excluded_canonical_ids.add(canonical_id)
        if title and title not in excluded_titles:
            excluded_titles.append(title)
        if theme and theme not in excluded_themes:
            excluded_themes.append(theme)
    return (
        excluded_passages[-8:],
        excluded_themes[-8:],
        excluded_titles[-8:],
        excluded_canonical_ids,
    )


def save_as_draft(emotion, res):
    try:
        DevotionalContent.objects.create(
            emotion=emotion,
            title=res.get('title', 'Rascunho de validacao'),
            scripture_reference=res.get('scripture_reference', ''),
            scripture_text=res.get('scripture_text', ''),
            reflection=res.get('reflection', ''),
            prayer=res.get('prayer', ''),
            share_quote=res.get('share_quote', ''),
            emotional_theme=res.get('emotional_theme', ''),
            is_active=False,
            reviewed_by_human=False,
            ai_generated=True,
        )
        print("  [DB] Salvo como rascunho — exclusions e cooldown acumulam.")
    except Exception as e:
        print(f"  [DB WARN] Nao foi possivel salvar rascunho: {e}")


def run_emotion(emotion, ai_service, n=GENERATIONS_PER_EMOTION):
    print(f"\n{'=' * 70}")
    print(f"  VALIDACAO: {emotion.name.upper()} — {n} GERACOES")
    print(f"{'=' * 70}")

    for i in range(1, n + 1):
        exc_passages, exc_themes, exc_titles, _ = build_exclusion_lists(emotion)
        semantic_cooldown = EditorialDevotionalGenerateView._build_semantic_cooldown(emotion)

        print(f"\n{'─' * 70}")
        print(f"  GERACAO {i}/{n}")
        print(f"{'─' * 70}")
        print(f"  Exclusions : {len(exc_passages)} passagens | {len(exc_themes)} temas | {len(exc_titles)} titulos")
        print(f"  Cooldown   : {', '.join(semantic_cooldown) if semantic_cooldown else '(nenhuma)'}")
        print(f"{'─' * 70}")

        res = ai_service.editorial_generate_devotional(
            emotion_name=emotion.name,
            excluded_passages=exc_passages,
            excluded_themes=exc_themes,
            excluded_titles=exc_titles,
            semantic_cooldown_words=semantic_cooldown,
        )

        print(f"\n  TITULO          : {res.get('title', '')}")
        print(f"  PASSAGEM        : {res.get('scripture_reference', '')}")
        print(f"  EMOTIONAL THEME : {res.get('emotional_theme', '')}")
        print(f"\n  TEXTO BIBLICO:\n  {res.get('scripture_text', '')}")
        print(f"\n  REFLEXAO:\n  {res.get('reflection', '')}")
        print(f"\n  ORACAO:\n  {res.get('prayer', '')}")
        print(f"\n  SHARE QUOTE:\n  \"{res.get('share_quote', '')}\"")

        save_as_draft(emotion, res)


def main():
    ai_service = get_ai_service()

    for slug, display_name in EMOTIONS_TO_TEST:
        try:
            emotion = Emotion.objects.get(slug=slug)
        except Emotion.DoesNotExist:
            # Tentar criar temporariamente para o teste
            print(f"\n[INFO] Emocao '{display_name}' (slug='{slug}') nao encontrada no banco.")
            try:
                emotion = Emotion.objects.create(name=display_name, slug=slug)
                print(f"[INFO] Emocao '{display_name}' criada temporariamente para validacao.")
            except Exception as e:
                print(f"[SKIP] Nao foi possivel criar '{display_name}': {e}")
                continue

        run_emotion(emotion, ai_service)

    print(f"\n{'=' * 70}")
    print("  FIM DA VALIDACAO COMPLETA.")
    print(f"{'=' * 70}\n")


if __name__ == '__main__':
    main()
