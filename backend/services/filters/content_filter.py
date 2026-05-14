from enum import Enum
from dataclasses import dataclass
from typing import Optional, List

class FilterAction(Enum):
    CLEAN = "clean"
    SOFT_FLAG = "soft_flag"
    HARD_BLOCK = "hard_block"

@dataclass
class FilterResult:
    action: FilterAction
    category: Optional[str] = None

class ContentFilter:
    # Termos explicitamente fora do escopo ou inaceitáveis
    HARD_BLOCK_TERMS: List[str] = [
        "sexo explícito", "pornografia", "matar", "suicídio", 
        "feitiçaria", "magia negra", "tarot", "horóscopo", "pacto",
        "blasfêmia", "odiar deus", "diabo"
    ]

    # Termos sensíveis que requerem cautela ou revisão, mas não bloqueio imediato
    SOFT_FLAG_TERMS: List[str] = [
        "política", "eleições", "presidente", "candidato",
        "outras religiões", "budismo", "islamismo", "kardecismo",
        "crise na igreja", "papa fez", "aborto",
        "dúvida de fé", "deus me abandonou", "não consigo rezar",
        "depressão", "ansiedade profunda", "crise de pânico"
    ]

    @classmethod
    def _check_text(cls, text: str) -> FilterResult:
        if not text:
            return FilterResult(action=FilterAction.CLEAN)
            
        text_lower = text.lower()
        
        # 1. Verifica HARD BLOCK primeiro
        for term in cls.HARD_BLOCK_TERMS:
            if term in text_lower:
                return FilterResult(action=FilterAction.HARD_BLOCK, category="inappropriate_content")
                
        # 2. Verifica SOFT FLAG
        for term in cls.SOFT_FLAG_TERMS:
            if term in text_lower:
                return FilterResult(action=FilterAction.SOFT_FLAG, category="sensitive_topic")
                
        # 3. CLEAN
        return FilterResult(action=FilterAction.CLEAN)

    @classmethod
    def check_input(cls, text: str) -> FilterResult:
        """Filtra o input do usuário antes de enviar para a IA."""
        return cls._check_text(text)

    @classmethod
    def check_output(cls, text: str) -> FilterResult:
        """Filtra a resposta gerada pela IA antes de entregar ao usuário."""
        return cls._check_text(text)

def get_fallback_for_hard_block() -> str:
    """Retorno padrão estático para quando um input ou output cai no HARD_BLOCK."""
    return (
        "O conteúdo solicitado aborda um tema que foge ao escopo pastoral e espiritual "
        "desta plataforma devocional católica, ou esbarra em temas inapropriados. "
        "Sugerimos conversar diretamente com um sacerdote ou diretor espiritual para orientações específicas."
    )
