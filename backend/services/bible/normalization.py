import re
from typing import Tuple, Optional

class NormalizationService:
    # Mapeamento simplificado para MVP
    BOOK_MAPPING = {
        'gn': 'GEN', 'genesis': 'GEN', 'gênesis': 'GEN',
        'ex': 'EXO', 'exodo': 'EXO', 'êxodo': 'EXO',
        'sl': 'PSA', 'salmo': 'PSA', 'salmos': 'PSA', 'psalm': 'PSA', 'psalms': 'PSA',
        'jo': 'JHN', 'joao': 'JHN', 'joão': 'JHN', 'john': 'JHN',
        'mt': 'MAT', 'mateus': 'MAT', 'matthew': 'MAT',
        'mc': 'MRK', 'marcos': 'MRK', 'mark': 'MRK',
        'lc': 'LUK', 'lucas': 'LUK', 'luke': 'LUK',
        'at': 'ACT', 'atos': 'ACT', 'acts': 'ACT',
        'rm': 'ROM', 'romanos': 'ROM', 'romans': 'ROM',
        'fp': 'PHP', 'filipenses': 'PHP', 'philippians': 'PHP',
        '1ts': '1TH', '1 tessalonicenses': '1TH', '1th': '1TH',
        # Adicionar mais conforme necessário
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
