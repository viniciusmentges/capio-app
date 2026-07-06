from django.db import migrations
import sys
import logging

logger = logging.getLogger(__name__)

def clean_asterisks(apps, schema_editor):
    if 'test' in sys.argv or 'test_coverage' in sys.argv:
        return
    try:
        DevotionalContent = apps.get_model('devotional', 'DevotionalContent')
        count = 0
        for dev in DevotionalContent.objects.all():
            modified = False
            for field in ['scripture_text', 'reflection', 'main_truth', 'daily_companion', 'prayer', 'share_quote']:
                val = getattr(dev, field, '')
                if val and isinstance(val, str) and '*' in val:
                    setattr(dev, field, val.replace('*', '').strip())
                    modified = True
            if modified:
                dev.save(update_fields=['scripture_text', 'reflection', 'main_truth', 'daily_companion', 'prayer', 'share_quote'])
                count += 1
        logger.info(f"[CAPIO EDITORIAL] {count} devocionais higienizados (asteriscos removidos).")
    except Exception as e:
        logger.error(f"Erro ao higienizar asteriscos na migration 0014: {e}")

class Migration(migrations.Migration):

    dependencies = [
        ('devotional', '0013_activate_editorial_library'),
    ]

    operations = [
        migrations.RunPython(clean_asterisks, migrations.RunPython.noop),
    ]
