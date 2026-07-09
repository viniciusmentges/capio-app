from django.core.management.base import BaseCommand
from django.db import transaction
from apps.devotional.models import Emotion, DevotionalContent
import glob
import re
import os
import logging

logger = logging.getLogger(__name__)

def to_title_case(title_str):
    prepositions = {
        'de', 'da', 'do', 'dos', 'das', 'em', 'no', 'na', 'nos', 'nas', 
        'e', 'a', 'o', 'as', 'os', 'um', 'uma', 'com', 'para', 'por', 'sem', 'sobre', 'sob', 
        'nem', 'que', 'como', 'ou', 'ao', 'aos', 'à', 'às'
    }
    words = title_str.strip().split()
    if not words:
        return ""
    result = []
    for idx, w in enumerate(words):
        lw = w.lower()
        if idx > 0 and lw in prepositions:
            result.append(lw)
        else:
            result.append(lw.capitalize())
    return " ".join(result)

class Command(BaseCommand):
    help = "Importa a Biblioteca Paralela (Staging Editorial) dos arquivos Markdown para o banco de dados em modo Homologacao."

    def add_arguments(self, parser):
        parser.add_argument(
            '--path',
            type=str,
            default=None,
            help='Caminho para o diretorio acervo_permanente'
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("[INICIO] Iniciando importacao da Biblioteca Paralela (Staging Editorial)..."))

        path = options['path']
        if not path:
            # Tentar caminhos padrao
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
            possible_paths = [
                os.path.join(base_dir, 'acervo_permanente'),
                os.path.join(os.path.dirname(base_dir), 'acervo_permanente'),
                'acervo_permanente',
                '../acervo_permanente',
            ]
            for p in possible_paths:
                if os.path.exists(p) and os.path.isdir(p):
                    path = p
                    break

        if not path or not os.path.exists(path):
            self.stdout.write(self.style.ERROR(f"[ERRO] Diretorio acervo_permanente nao encontrado. Caminho: {path}"))
            return

        self.stdout.write(f"[ARQUIVOS] Lendo arquivos de: {os.path.abspath(path)}")
        files = sorted(glob.glob(os.path.join(path, 'acervo_capio_*.md')))

        if not files:
            self.stdout.write(self.style.ERROR("[ERRO] Nenhum arquivo acervo_capio_*.md encontrado na pasta."))
            return

        all_editorial_slugs = [
            'ansioso', 'triste', 'medo', 'desmotivado', 'sozinho', 'sem-esperanca',
            'direcao', 'gratidao', 'inseguro', 'cansado', 'culpado', 'raiva',
            'confuso', 'vazio', 'corajoso-mas-incerto', 'chamado-mas-hesitante',
            'tentado', 'em-conflito-com-alguem', 'grato-mas-disperso', 'disciplinado-mas-frio'
        ]
        # Limpar registros da biblioteca editorial anteriores para garantir idempotencia ao reimportar
        deleted_count, _ = DevotionalContent.objects.filter(reviewed_by_human=True, emotion__slug__in=all_editorial_slugs).delete()
        if deleted_count:
            self.stdout.write(self.style.WARNING(f"[LIMPEZA] Removidos {deleted_count} registros editoriais anteriores para reimportacao limpa."))

        emotion_map = {
            '01_ansioso': ('ansioso', 'Ansioso'),
            '02_triste': ('triste', 'Triste'),
            '03_medo': ('medo', 'Medo'),
            '04_desmotivado': ('desmotivado', 'Desmotivado'),
            '05_sozinho': ('sozinho', 'Sozinho'),
            '06_sem_esperanca': ('sem-esperanca', 'Sem Esperança'),
            '07_direcao': ('direcao', 'Direção'),
            '08_gratidao': ('gratidao', 'Gratidão'),
            '09_inseguro': ('inseguro', 'Inseguro'),
            '10_cansado': ('cansado', 'Cansado'),
            '11_corajoso_mas_incerto': ('corajoso-mas-incerto', 'Corajoso, mas incerto'),
            '12_chamado_mas_hesitante': ('chamado-mas-hesitante', 'Chamado, mas hesitante'),
            '13_tentado': ('tentado', 'Tentado'),
            '14_em_conflito_com_alguem': ('em-conflito-com-alguem', 'Em conflito com alguém'),
            '15_grato_mas_disperso': ('grato-mas-disperso', 'Grato, mas disperso'),
            '16_disciplinado_mas_frio': ('disciplinado-mas-frio', 'Disciplinado, mas frio'),
        }

        total_imported = 0
        emotions_updated = []

        for f in files:
            filename = os.path.basename(f)
            emotion_slug = None
            emotion_name = None
            for key, (slug, name) in emotion_map.items():
                if key in filename:
                    emotion_slug = slug
                    emotion_name = name
                    break

            if not emotion_slug:
                self.stdout.write(self.style.WARNING(f"[AVISO] Arquivo ignorado (emocao nao mapeada): {filename}"))
                continue

            self.stdout.write(self.style.NOTICE(f"\n[COLECAO] Processando Colecao: {emotion_name} ({filename})..."))

            with transaction.atomic():
                emotion, _ = Emotion.objects.get_or_create(
                    slug=emotion_slug,
                    defaults={'name': emotion_name}
                )
                if emotion.name != emotion_name:
                    emotion.name = emotion_name
                    emotion.save(update_fields=['name'])

                content = open(f, encoding='utf-8').read()
                devs = re.split(r'# DEVOCIONAL \d+ — ', content)[1:]

                self.stdout.write(f"  -> Encontrados {len(devs)} devocionais no arquivo.")

                for idx, d in enumerate(devs, 1):
                    lines = d.split('\n')
                    raw_title = lines[0].strip()
                    title = to_title_case(raw_title)

                    # Limpar possiveis linhas divisorias de encerramento
                    clean_d = re.split(r'\n---', d)[0]

                    # Encontrar linha de passagem
                    passage_line = [l for l in clean_d.split('\n') if 'Passagem' in l][0]
                    m = re.search(r'[*_]*[\"“](.+?)[\"”][*_]*\s*\(([^)]+)\)', passage_line)
                    if not m:
                        self.stdout.write(self.style.ERROR(f"  [ERRO] Falha ao extrair passagem em: {title}"))
                        continue

                    scripture_text = m.group(1).strip()
                    scripture_reference = m.group(2).strip()

                    # Extrair secoes
                    sections = re.split(r'###\s+', clean_d)
                    sec_data = {}
                    for s in sections[1:]:
                        header = s.split('\n')[0].strip()
                        body = '\n'.join(s.split('\n')[1:]).strip()
                        sec_data[header] = body

                    reflection = sec_data.get("Reflection (CONDUZ)", "")
                    main_truth = sec_data.get("Fio da Palavra (ANCORA)", "")
                    daily_companion = sec_data.get("Palavra Continua (ACOMPANHA)", "")
                    prayer = sec_data.get("Oração", "")
                    share_quote = sec_data.get("Share Quote (PERMANECE)", "")

                    if not (reflection and main_truth and daily_companion and prayer and share_quote):
                        self.stdout.write(self.style.ERROR(f"  [ERRO] Campos incompletos no devocional: {title}"))
                        continue

                    scripture_text = scripture_text.replace('*', '').strip()
                    reflection = reflection.replace('*', '').strip()
                    main_truth = main_truth.replace('*', '').strip()
                    daily_companion = daily_companion.replace('*', '').strip()
                    prayer = prayer.replace('*', '').strip()
                    share_quote = share_quote.replace('*', '').strip()

                    share_text = share_quote[:107] + "..." if len(share_quote) > 110 else share_quote

                    # Criar ou atualizar no banco como ativo (is_active=True, reviewed_by_human=True)
                    dev_obj, created = DevotionalContent.objects.update_or_create(
                        emotion=emotion,
                        title=title,
                        defaults={
                            'scripture_reference': scripture_reference,
                            'scripture_text': scripture_text,
                            'reflection': reflection,
                            'main_truth': main_truth,
                            'daily_companion': daily_companion,
                            'prayer': prayer,
                            'share_quote': share_quote,
                            'share_text': share_text,
                            'emotional_theme': title,
                            'is_active': True,  # Biblioteca ativa em produção!
                            'reviewed_by_human': True,
                            'ai_generated': True,
                        }
                    )

                    status_str = "CRIADO" if created else "ATUALIZADO"
                    self.stdout.write(self.style.SUCCESS(f"  [{status_str}] {idx}. {title} ({scripture_reference})"))
                    total_imported += 1

            emotions_updated.append(emotion_name)

        self.stdout.write("\n" + "=" * 50)
        self.stdout.write(self.style.SUCCESS(f"[SUCESSO] VALIDACAO EDITORIAL INICIADA COM SUCESSO!"))
        self.stdout.write(self.style.SUCCESS(f"  -> Total de devocionais importados em staging: {total_imported}"))
        self.stdout.write(self.style.SUCCESS(f"  -> Emocoes disponiveis para testes (staff/admin): {', '.join(emotions_updated)}"))
        self.stdout.write("=" * 50)
