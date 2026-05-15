import re
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

    @classmethod
    def normalize(cls, reference: str) -> Tuple[str, str, int, Optional[str]]:
        """
        Retorna (canonical_id, book_name, chapter, verses)
        """
        ref = reference.lower().strip()
        # Jo 3:16 -> book="jo", rest="3:16"
        # 1 Tessalonicenses 5:18 -> book="1 tessalonicenses", rest="5:18"
        
        # Regex para separar livro de capítulo/versículo
        # Pega o último espaço ou a transição para número
        match = re.match(r'^(.+?)\s*(\d+.*)$', ref)
        if not match:
            return ref.upper(), ref.title(), 0, None
            
        book_raw = match.group(1).strip()
        rest = match.group(2).strip()
        
        book_id = cls.BOOK_MAPPING.get(book_raw, book_raw.upper()[:3])
        
        # Tratar capítulo e versículos (3:16 ou 3,16 ou 3 16)
        rest = rest.replace(',', ':').replace(' ', ':')
        parts = rest.split(':')
        chapter = int(parts[0]) if parts[0].isdigit() else 0
        verses = parts[1] if len(parts) > 1 else None
        
        canonical_id = f"{book_id}.{chapter}"
        if verses:
            canonical_id += f":{verses}"
            
        return canonical_id, book_raw.title(), chapter, verses
