import os
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.contrib.auth import get_user_model
import environ
from django.conf import settings
import json
from apps.devotional.models import Emotion, DevotionalContent

User = get_user_model()

class Command(BaseCommand):
    help = 'Seeds initial data for the application'

    def handle(self, *args, **options):
        self.stdout.write('Starting seed process...')

        # 1. Load emotions
        emotions_path = os.path.join(settings.BASE_DIR, 'fixtures', 'emotions.json')
        if os.path.exists(emotions_path):
            self.stdout.write('Loading emotions...')
            call_command('loaddata', emotions_path)
            self.stdout.write(self.style.SUCCESS('Emotions loaded successfully.'))
        else:
            self.stdout.write(self.style.WARNING('Emotions fixture not found. Skipping.'))

        # 2. Check mock fixtures
        mock_dir = os.path.join(settings.BASE_DIR, 'fixtures', 'mock_responses')
        if os.path.exists(mock_dir):
            self.stdout.write(self.style.SUCCESS('Mock fixtures directory found.'))
            
            ansioso_path = os.path.join(mock_dir, 'devotional', 'ansioso_batch.json')
            if os.path.exists(ansioso_path):
                self.stdout.write('Loading ansioso devotionals...')
                emotion, _ = Emotion.objects.get_or_create(
                    slug='ansioso',
                    defaults={'name': 'Ansioso', 'icon': ''}
                )
                
                with open(ansioso_path, 'r', encoding='utf-8') as f:
                    devotionals = json.load(f)
                    created_count = 0
                    for item in devotionals:
                        _, created = DevotionalContent.objects.get_or_create(
                            emotion=emotion,
                            title=item['title'],
                            scripture_reference=item['scripture_reference'],
                            defaults={
                                'scripture_text': item['scripture_text'],
                                'reflection': item['reflection'],
                                'prayer': item['prayer'],
                                'is_active': True,
                                'ai_generated': False
                            }
                        )
                        if created:
                            created_count += 1
                self.stdout.write(self.style.SUCCESS(f'Created {created_count} new devotionals for "ansioso".'))
            
            # Load triste_batch.json
            triste_path = os.path.join(mock_dir, 'devotional', 'triste_batch.json')
            if os.path.exists(triste_path):
                self.stdout.write('Loading triste devotionals...')
                emotion_triste, _ = Emotion.objects.get_or_create(
                    slug='triste',
                    defaults={'name': 'Triste', 'icon': ''}
                )
                
                with open(triste_path, 'r', encoding='utf-8') as f:
                    devotionals_triste = json.load(f)
                    created_count_triste = 0
                    for item in devotionals_triste:
                        _, created = DevotionalContent.objects.get_or_create(
                            emotion=emotion_triste,
                            title=item['title'],
                            scripture_reference=item['scripture_reference'],
                            defaults={
                                'scripture_text': item['scripture_text'],
                                'reflection': item['reflection'],
                                'prayer': item['prayer'],
                                'is_active': True,
                                'ai_generated': False
                            }
                        )
                        if created:
                            created_count_triste += 1
                self.stdout.write(self.style.SUCCESS(f'Created {created_count_triste} new devotionals for "triste".'))
            
            # Load medo_batch.json
            medo_path = os.path.join(mock_dir, 'devotional', 'medo_batch.json')
            if os.path.exists(medo_path):
                self.stdout.write('Loading medo devotionals...')
                emotion_medo, _ = Emotion.objects.get_or_create(
                    slug='medo',
                    defaults={'name': 'Medo', 'icon': ''}
                )
                
                with open(medo_path, 'r', encoding='utf-8') as f:
                    devotionals_medo = json.load(f)
                    created_count_medo = 0
                    for item in devotionals_medo:
                        _, created = DevotionalContent.objects.get_or_create(
                            emotion=emotion_medo,
                            title=item['title'],
                            scripture_reference=item['scripture_reference'],
                            defaults={
                                'scripture_text': item['scripture_text'],
                                'reflection': item['reflection'],
                                'prayer': item['prayer'],
                                'is_active': True,
                                'ai_generated': False
                            }
                        )
                        if created:
                            created_count_medo += 1
                self.stdout.write(self.style.SUCCESS(f'Created {created_count_medo} new devotionals for "medo".'))

            # Load desmotivado_batch.json
            desmotivado_path = os.path.join(mock_dir, 'devotional', 'desmotivado_batch.json')
            if os.path.exists(desmotivado_path):
                self.stdout.write('Loading desmotivado devotionals...')
                emotion_desmotivado, _ = Emotion.objects.get_or_create(
                    slug='desmotivado',
                    defaults={'name': 'Desmotivado', 'icon': ''}
                )
                
                with open(desmotivado_path, 'r', encoding='utf-8') as f:
                    devotionals_desmotivado = json.load(f)
                    created_count_desmotivado = 0
                    for item in devotionals_desmotivado:
                        _, created = DevotionalContent.objects.get_or_create(
                            emotion=emotion_desmotivado,
                            title=item['title'],
                            scripture_reference=item['scripture_reference'],
                            defaults={
                                'scripture_text': item['scripture_text'],
                                'reflection': item['reflection'],
                                'prayer': item['prayer'],
                                'is_active': True,
                                'ai_generated': False
                            }
                        )
                        if created:
                            created_count_desmotivado += 1
                self.stdout.write(self.style.SUCCESS(f'Created {created_count_desmotivado} new devotionals for "desmotivado".'))

            # Load sozinho_batch.json
            sozinho_path = os.path.join(mock_dir, 'devotional', 'sozinho_batch.json')
            if os.path.exists(sozinho_path):
                self.stdout.write('Loading sozinho devotionals...')
                emotion_sozinho, _ = Emotion.objects.get_or_create(
                    slug='sozinho',
                    defaults={'name': 'Sozinho', 'icon': ''}
                )
                
                with open(sozinho_path, 'r', encoding='utf-8') as f:
                    devotionals_sozinho = json.load(f)
                    created_count_sozinho = 0
                    for item in devotionals_sozinho:
                        _, created = DevotionalContent.objects.get_or_create(
                            emotion=emotion_sozinho,
                            title=item['title'],
                            scripture_reference=item['scripture_reference'],
                            defaults={
                                'scripture_text': item['scripture_text'],
                                'reflection': item['reflection'],
                                'prayer': item['prayer'],
                                'is_active': True,
                                'ai_generated': False
                            }
                        )
                        if created:
                            created_count_sozinho += 1
                self.stdout.write(self.style.SUCCESS(f'Created {created_count_sozinho} new devotionals for "sozinho".'))

            # Load sem_esperanca_batch.json
            sem_esperanca_path = os.path.join(mock_dir, 'devotional', 'sem_esperanca_batch.json')
            if os.path.exists(sem_esperanca_path):
                self.stdout.write('Loading sem_esperanca devotionals...')
                emotion_sem_esperanca, _ = Emotion.objects.get_or_create(
                    slug='sem-esperanca',
                    defaults={'name': 'Sem Esperança', 'icon': ''}
                )
                
                with open(sem_esperanca_path, 'r', encoding='utf-8') as f:
                    devotionals_sem_esperanca = json.load(f)
                    created_count_sem_esperanca = 0
                    for item in devotionals_sem_esperanca:
                        _, created = DevotionalContent.objects.get_or_create(
                            emotion=emotion_sem_esperanca,
                            title=item['title'],
                            scripture_reference=item['scripture_reference'],
                            defaults={
                                'scripture_text': item['scripture_text'],
                                'reflection': item['reflection'],
                                'prayer': item['prayer'],
                                'is_active': True,
                                'ai_generated': False
                            }
                        )
                        if created:
                            created_count_sem_esperanca += 1
                self.stdout.write(self.style.SUCCESS(f'Created {created_count_sem_esperanca} new devotionals for "sem_esperanca".'))

            # Load direcao_batch.json
            direcao_path = os.path.join(mock_dir, 'devotional', 'direcao_batch.json')
            if os.path.exists(direcao_path):
                self.stdout.write('Loading direcao devotionals...')
                emotion_direcao, _ = Emotion.objects.get_or_create(
                    slug='direcao',
                    defaults={'name': 'Direção', 'icon': ''}
                )
                
                with open(direcao_path, 'r', encoding='utf-8') as f:
                    devotionals_direcao = json.load(f)
                    created_count_direcao = 0
                    for item in devotionals_direcao:
                        _, created = DevotionalContent.objects.get_or_create(
                            emotion=emotion_direcao,
                            title=item['title'],
                            scripture_reference=item['scripture_reference'],
                            defaults={
                                'scripture_text': item['scripture_text'],
                                'reflection': item['reflection'],
                                'prayer': item['prayer'],
                                'is_active': True,
                                'ai_generated': False
                            }
                        )
                        if created:
                            created_count_direcao += 1
                self.stdout.write(self.style.SUCCESS(f'Created {created_count_direcao} new devotionals for "direcao".'))

            # Load gratidao_batch.json
            gratidao_path = os.path.join(mock_dir, 'devotional', 'gratidao_batch.json')
            if os.path.exists(gratidao_path):
                self.stdout.write('Loading gratidao devotionals...')
                emotion_gratidao, _ = Emotion.objects.get_or_create(
                    slug='gratidao',
                    defaults={'name': 'Gratidão', 'icon': ''}
                )
                
                with open(gratidao_path, 'r', encoding='utf-8') as f:
                    devotionals_gratidao = json.load(f)
                    created_count_gratidao = 0
                    for item in devotionals_gratidao:
                        _, created = DevotionalContent.objects.get_or_create(
                            emotion=emotion_gratidao,
                            title=item['title'],
                            scripture_reference=item['scripture_reference'],
                            defaults={
                                'scripture_text': item['scripture_text'],
                                'reflection': item['reflection'],
                                'prayer': item['prayer'],
                                'is_active': True,
                                'ai_generated': False
                            }
                        )
                        if created:
                            created_count_gratidao += 1
                self.stdout.write(self.style.SUCCESS(f'Created {created_count_gratidao} new devotionals for "gratidao".'))
                
        else:
            self.stdout.write(self.style.WARNING('Mock fixtures directory not found.'))

        # 3. Create Admin User (if env configured)
        env = environ.Env()
        admin_user = env.str('DJANGO_ADMIN_USER', default='admin')
        admin_pass = env.str('DJANGO_ADMIN_PASSWORD', default='admin123')
        admin_email = env.str('DJANGO_ADMIN_EMAIL', default='admin@admin.com')

        if not User.objects.filter(username=admin_user).exists():
            User.objects.create_superuser(username=admin_user, email=admin_email, password=admin_pass)
            self.stdout.write(self.style.SUCCESS(f'Superuser {admin_user} created.'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Superuser {admin_user} already exists.'))

        self.stdout.write(self.style.SUCCESS('Seed completed successfully.'))
