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
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
            possible_paths = [
                os.path.join(base_dir, 'acervo_permanente'),
                os.path.join(os.path.dirname(base_dir), 'acervo_permanente'),
                os.path.join(os.path.dirname(os.path.dirname(base_dir)), 'acervo_permanente'),
                '/opt/render/project/src/acervo_permanente',
                '/opt/render/project/acervo_permanente',
                '/opt/render/project/src/backend/acervo_permanente',
                'acervo_permanente',
                '../acervo_permanente',
                '../../acervo_permanente',
            ]
            for p in possible_paths:
                if os.path.exists(p) and os.path.isdir(p):
                    path = p
                    break

        if not path or not os.path.exists(path):
            self.stdout.write(self.style.ERROR(f"[ERRO] Diretorio acervo_permanente nao encontrado. Caminho procurado em: {possible_paths}"))
            return

        self.stdout.write(f"[ARQUIVOS] Lendo arquivos de: {os.path.abspath(path)}")
        files = sorted(glob.glob(os.path.join(path, 'acervo_capio_*.md')))

        if not files:
            self.stdout.write(self.style.ERROR("[ERRO] Nenhum arquivo acervo_capio_*.md encontrado na pasta."))
            return

        # Construcao Dinamica das Emocoes
        emotion_map = {}
        all_editorial_slugs = []
        
        for f in files:
            filename = os.path.basename(f)
            m = re.match(r'acervo_capio_\d+_(.*)\.md', filename)
            if not m:
                continue
                
            raw_slug = m.group(1)
            slug = raw_slug.replace('_', '-')
            icon = f"{raw_slug}_icon"
            
            # Ler o nome correto da emocao direto do arquivo
            content_preview = open(f, encoding='utf-8').read(500)
            header_match = re.search(r'# ACERVO EDITORIAL CAPIO — COLEÇÃO \d+: (.*)', content_preview, re.IGNORECASE)
            
            if header_match:
                name = header_match.group(1).strip().capitalize()
            else:
                # Fallback
                name = raw_slug.replace('_', ' ').capitalize()
                
            emotion_map[filename] = (slug, name, icon)
            all_editorial_slugs.append(slug)

        # Limpeza
        deleted_count, _ = DevotionalContent.objects.filter(reviewed_by_human=True, emotion__slug__in=all_editorial_slugs).delete()
        if deleted_count:
            self.stdout.write(self.style.WARNING(f"[LIMPEZA] Removidos {deleted_count} registros editoriais anteriores para reimportacao limpa."))

        total_imported = 0
        emotions_updated = []

        for f in files:
            filename = os.path.basename(f)
            if filename not in emotion_map:
                self.stdout.write(self.style.WARNING(f"[AVISO] Arquivo ignorado (nao mapeado): {filename}"))
                continue
                
            emotion_slug, emotion_name, emotion_icon = emotion_map[filename]

            self.stdout.write(self.style.NOTICE(f"\n[COLECAO] Processando Colecao: {emotion_name} ({filename})..."))

            with transaction.atomic():
                emotion, _ = Emotion.objects.get_or_create(
                    slug=emotion_slug,
                    defaults={'name': emotion_name, 'icon': emotion_icon}
                )
                if emotion.name != emotion_name or emotion.icon != emotion_icon:
                    emotion.name = emotion_name
                    emotion.icon = emotion_icon
                    emotion.save(update_fields=['name', 'icon'])

                content = open(f, encoding='utf-8').read()
                devs = re.split(r'# DEVOCIONAL \d+ — ', content)[1:]

                self.stdout.write(f"  -> Encontrados {len(devs)} devocionais no arquivo.")

                for idx, d in enumerate(devs, 1):
                    lines = d.split('\n')
                    raw_title = lines[0].strip()
                    title = to_title_case(raw_title)

                    clean_d = re.split(r'\n---', d)[0]

                    passage_line_matches = [l for l in clean_d.split('\n') if 'Passagem' in l]
                    if not passage_line_matches:
                        self.stdout.write(self.style.ERROR(f"  [ERRO] Linha de passagem nao encontrada em: {title}"))
                        continue
                        
                    passage_line = passage_line_matches[0]
                    m = re.search(r'[*_]*[\"“](.+?)[\"”][*_]*\s*\(([^)]+)\)', passage_line)
                    if not m:
                        self.stdout.write(self.style.ERROR(f"  [ERRO] Falha ao extrair passagem em: {title}"))
                        continue

                    scripture_text = m.group(1).strip()
                    scripture_reference = m.group(2).strip()

                    sections = re.split(r'###\s+', clean_d)
                    sec_data = {}
                    for s in sections[1:]:
                        header = s.split('\n')[0].strip()
                        body = '\n'.join(s.split('\n')[1:]).strip()
                        sec_data[header] = body

                    def get_section(names):
                        for k, v in sec_data.items():
                            clean_k = k.strip().lower()
                            for name in names:
                                if name.lower() in clean_k:
                                    return v
                        return ""

                    reflection = get_section(["reflection (conduz)", "reflection"])
                    anchor_text = get_section(["fio da palavra", "ancora", "âncora"])
                    carry_with_you = get_section(["leve com você", "leve com voce", "ponto de contato", "toca"])
                    word_continues = get_section(["palavra continua", "palavra contínua", "acompanha"])
                    prayer = get_section(["oração", "oracao"])
                    share_quote = get_section(["share quote", "permanece"])

                    missing_sections = []
                    if not anchor_text: missing_sections.append("Fio da Palavra")
                    if not carry_with_you: missing_sections.append("Leve com Você")
                    if not word_continues: missing_sections.append("A Palavra Continua")
                    if not reflection: missing_sections.append("Reflection")
                    
                    if missing_sections:
                        self.stdout.write(self.style.WARNING(f"  [AVISO] Seções ausentes em '{title}': {', '.join(missing_sections)}"))

                    scripture_text = scripture_text.replace('*', '').strip()
                    reflection = reflection.replace('*', '').strip()
                    anchor_text = anchor_text.replace('*', '').strip()
                    carry_with_you = carry_with_you.replace('*', '').strip()
                    word_continues = word_continues.replace('*', '').strip()
                    prayer = prayer.replace('*', '').strip()
                    share_quote = share_quote.replace('*', '').strip()

                    share_text = share_quote[:107] + "..." if len(share_quote) > 110 else share_quote

                    dev_obj, created = DevotionalContent.objects.update_or_create(
                        emotion=emotion,
                        title=title,
                        defaults={
                            'scripture_reference': scripture_reference,
                            'scripture_text': scripture_text,
                            'reflection': reflection,
                            'anchor_text': anchor_text,
                            'carry_with_you_text': carry_with_you,
                            'word_continues_text': word_continues,
                            'main_truth': anchor_text,
                            'daily_companion': word_continues,
                            'prayer': prayer,
                            'share_quote': share_quote,
                            'share_text': share_text,
                            'emotional_theme': title,
                            'is_active': True,
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
