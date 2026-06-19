import re
import unicodedata
from typing import Tuple, Optional

class NormalizationService:
    # Mapeamento simplificado para MVP
    BOOK_MAPPING = {
        'gn': 'GEN', 'genesis': 'GEN', 'gênesis': 'GEN',
        'ex': 'EXO', 'exodo': 'EXO', 'êxodo': 'EXO',
        'lv': 'LEV', 'levitico': 'LEV', 'levítico': 'LEV',
        'nm': 'NUM', 'numeros': 'NUM', 'números': 'NUM',
        'dt': 'DEU', 'deuteronomio': 'DEU', 'deuteronômio': 'DEU',
        'js': 'JOS', 'josue': 'JOS', 'josué': 'JOS',
        'jz': 'JDG', 'juizes': 'JDG', 'juízes': 'JDG',
        'rt': 'RUT', 'rute': 'RUT',
        '1sm': '1SA', '1 samuel': '1SA',
        '2sm': '2SA', '2 samuel': '2SA',
        '1rs': '1KI', '1 reis': '1KI',
        '2rs': '2KI', '2 reis': '2KI',
        '1cr': '1CH', '1 cronicas': '1CH',
        '2cr': '2CH', '2 cronicas': '2CH',
        'ed': 'EZR', 'esdras': 'EZR',
        'ne': 'NEH', 'neemias': 'NEH',
        'et': 'EST', 'ester': 'EST',
        'jô': 'JOB', 'jo': 'JOB', # Conflito com João tratado via contexto ou prioridade
        'sl': 'PSA', 'salmo': 'PSA', 'salmos': 'PSA', 'psalm': 'PSA', 'psalms': 'PSA',
        'pv': 'PRO', 'proverbios': 'PRO', 'provérbios': 'PRO',
        'ec': 'ECC', 'eclesiastes': 'ECC',
        'ct': 'SNG', 'canticos': 'SNG', 'cânticos': 'SNG',
        'is': 'ISA', 'isaias': 'ISA', 'isaías': 'ISA',
        'jr': 'JER', 'jeremias': 'JER',
        'lm': 'LAM', 'lamentacoes': 'LAM', 'lamentações': 'LAM',
        'ez': 'EZK', 'ezequiel': 'EZK',
        'dn': 'DAN', 'daniel': 'DAN',
        'os': 'HOS', 'oseias': 'HOS', 'oseias': 'HOS',
        'jl': 'JOE', 'joel': 'JOE',
        'am': 'AMO', 'amos': 'AMO',
        'ob': 'OBA', 'obadias': 'OBA',
        'mq': 'MIC', 'miqueias': 'MIC',
        'na': 'NAH', 'naum': 'NAH',
        'hc': 'HAB', 'habacuque': 'HAB',
        'sf': 'ZEP', 'sofonias': 'ZEP',
        'ag': 'HAG', 'ageu': 'HAG',
        'zc': 'ZEC', 'zacarias': 'ZEC',
        'ml': 'MAL', 'malaquias': 'MAL',
        'mt': 'MAT', 'mateus': 'MAT', 'matthew': 'MAT',
        'mc': 'MRK', 'marcos': 'MRK', 'mark': 'MRK',
        'lc': 'LUK', 'lucas': 'LUK', 'luke': 'LUK',
        'jo': 'JHN', 'joao': 'JHN', 'joão': 'JHN', 'john': 'JHN',
        'at': 'ACT', 'atos': 'ACT', 'acts': 'ACT',
        'rm': 'ROM', 'romanos': 'ROM', 'romans': 'ROM',
        '1co': '1CO', '1 corintios': '1CO',
        '2co': '2CO', '2 corintios': '2CO',
        'gl': 'GAL', 'galatas': 'GAL',
        'ef': 'EPH', 'efesios': 'EPH',
        'fp': 'PHP', 'filipenses': 'PHP', 'philippians': 'PHP',
        'cl': 'COL', 'colossenses': 'COL',
        '1ts': '1TH', '1 tessalonicenses': '1TH', '1th': '1TH',
        '2ts': '2TH', '2 tessalonicenses': '2TH',
        '1tm': '1TI', '1 timoteo': '1TI',
        '2tm': '2TI', '2 timoteo': '2TI',
        'tt': 'TIT', 'tito': 'TIT',
        'fm': 'PHM', 'filemon': 'PHM',
        'hb': 'HEB', 'hebreus': 'HEB',
        'tg': 'JAS', 'tiago': 'JAS',
        '1pe': '1PE', '1 pedro': '1PE',
        '2pe': '2PE', '2 pedro': '2PE',
        '1jo': '1JN', '1 joao': '1JN',
        '2jo': '2JN', '2 joao': '2JN',
        '3jo': '3JN', '3 joao': '3JN',
        'jd': 'JUD', 'judas': 'JUD',
        'ap': 'REV', 'apocalipse': 'REV', 'revelation': 'REV',
    }

    CHAPTER_COUNTS = {
        'GEN': 50, 'EXO': 40, 'LEV': 27, 'NUM': 36, 'DEU': 34,
        'JOS': 24, 'JDG': 21, 'RUT': 4, '1SA': 31, '2SA': 24,
        '1KI': 22, '2KI': 25, '1CH': 29, '2CH': 36, 'EZR': 10,
        'NEH': 13, 'EST': 10, 'JOB': 42, 'PSA': 150, 'PRO': 31,
        'ECC': 12, 'SNG': 8, 'ISA': 66, 'JER': 52, 'LAM': 5,
        'EZK': 48, 'DAN': 12, 'HOS': 14, 'JOE': 3, 'AMO': 9,
        'OBA': 1, 'MIC': 7, 'NAH': 3, 'HAB': 3, 'ZEP': 3,
        'HAG': 2, 'ZEC': 14, 'MAL': 4, 'MAT': 28, 'MRK': 16,
        'LUK': 24, 'JHN': 21, 'ACT': 28, 'ROM': 16, '1CO': 16,
        '2CO': 13, 'GAL': 6, 'EPH': 6, 'PHP': 4, 'COL': 4,
        '1TH': 5, '2TH': 3, '1TI': 6, '2TI': 4, 'TIT': 3,
        'PHM': 1, 'HEB': 13, 'JAS': 5, '1PE': 5, '2PE': 3,
        '1JN': 5, '2JN': 1, '3JN': 1, 'JUD': 1, 'REV': 22
    }

    @classmethod
    def _remove_accents(cls, text: str) -> str:
        text = unicodedata.normalize('NFD', text)
        return ''.join(c for c in text if unicodedata.category(c) != 'Mn')

    @classmethod
    def is_valid_reference(cls, reference: str) -> bool:
        """
        Valida se a entrada contém apenas uma referência bíblica válida (Livro + opcionais Capítulo/Versículo).
        Impede entradas emocionais (ex: "estou sofrendo igual Jó" ou "preciso de um salmo para ansiedade").
        """
        ref = cls._remove_accents(reference.lower().strip())
        
        # Regex rigorosa: A string inteira deve ser (Livro) opcionalmente seguido de espaços e (Capitulo/Versículo)
        # ^([a-zà-ú0-9\s]+?)(?:\s+(\d+[\d:.,\s\-]*))?$
        # Isso garante que não haja palavras soltas no final
        match = re.match(r'^([a-z0-9\s]+?)(?:\s+(\d+[\d:.,\s\-]*))?$', ref)
        if not match:
            return False
            
        book_raw = match.group(1).strip()
        return book_raw in cls.BOOK_MAPPING

    @classmethod
    def normalize(cls, reference: str) -> Tuple[str, str, int, Optional[str]]:
        """
        Retorna (canonical_id, book_name, chapter, verses)
        A partir de agora, canonical_id representa sempre O CAPÍTULO INTEIRO.
        """
        ref_clean = cls._remove_accents(reference.lower().strip())
        # Regex para separar livro de capítulo/versículo
        match = re.match(r'^(.+?)\s*(\d+.*)$', ref_clean)
        if not match:
            return reference.upper().strip(), reference.title().strip(), 0, None
            
        book_raw = match.group(1).strip()
        rest = match.group(2).strip()
        
        book_id = cls.BOOK_MAPPING.get(book_raw, book_raw.upper()[:3])
        
        # Tratar capítulo e versículos (ex: 3:16 ou 3,16 ou 3 16 ou 6:10-18)
        rest = rest.replace(',', ':').replace(' ', ':')
        parts = rest.split(':', 1) # Split only on first colon
        chapter = int(parts[0]) if parts[0].isdigit() else 0
        verses = parts[1].strip() if len(parts) > 1 else None
        
        # canonical_id agora é sempre a nível de capítulo (ex: MAT.8)
        canonical_id = f"{book_id}.{chapter}"
        
        # Usamos o nome original enviado pelo usuário para exibição
        match_orig = re.match(r'^(.+?)\s*(\d+.*)$', reference.strip())
        book_display = match_orig.group(1).strip().title() if match_orig else book_raw.title()
            
        return canonical_id, book_display, chapter, verses
