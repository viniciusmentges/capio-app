import logging
import re
from datetime import date, timedelta
from collections import Counter
from django.utils import timezone
from apps.reflection.models import DailyReflection
from services.reflection.reflection_service import DAILY_REFLECTION_THEMES

logger = logging.getLogger(__name__)

# Livros do Novo Testamento em português para classificação Canônica (NT vs AT)
NT_BOOKS = {
    "mateus", "marcos", "lucas", "joao", "joão", "atos", "romanos",
    "1 corintios", "1 coríntios", "2 corintios", "2 coríntios",
    "galatas", "gálatas", "efesios", "efésios", "filipenses",
    "colossenses", "1 tessalonicenses", "2 tessalonicenses",
    "1 timoteo", "1 timóteo", "2 timoteo", "2 timóteo",
    "tito", "filemom", "filemon", "hebreus", "tiago",
    "1 pedro", "2 pedro", "1 joao", "1 joão", "2 joao", "2 joão",
    "3 joao", "3 joão", "judas", "apocalipse"
}

def _calculate_jaccard_similarity(str1: str, str2: str) -> float:
    """
    Calcula a similaridade de Jaccard entre dois textos baseando-se em tokens limpos.
    Ignora palavras curtas e pontuações para focar na semântica principal.
    """
    def get_tokens(text):
        if not text:
            return set()
        # Remove pontuações e converte para minúsculo
        cleaned = re.sub(r'[^\w\s]', '', text.lower())
        words = cleaned.split()
        # Filtra stop words muito simples de tamanho <= 2
        return {w for w in words if len(w) > 2}

    set1 = get_tokens(str1)
    set2 = get_tokens(str2)
    
    if not set1 or not set2:
        return 0.0
        
    intersection = set1.intersection(set2)
    union = set1.union(set2)
    return len(intersection) / len(union)

def get_theme_distribution(days=30):
    """
    Retorna a distribuição percentual e absoluta dos eixos temáticos gerados.
    """
    end_date = timezone.localtime().date()
    start_date = end_date - timedelta(days=days)
    
    reflections = DailyReflection.objects.filter(
        date__range=(start_date, end_date)
    ).exclude(theme_key="")
    
    total_count = reflections.count()
    
    theme_counts = Counter(reflections.values_list("theme_key", flat=True))
    
    distribution = {}
    for key, count in theme_counts.items():
        # Busca detalhes legíveis do tema
        theme_meta = next((t for t in DAILY_REFLECTION_THEMES if t["key"] == key), None)
        label = theme_meta["label"] if theme_meta else key.capitalize()
        
        dates_used = list(reflections.filter(theme_key=key).order_by("date").values_list("date", flat=True))
        dates_formatted = [d.isoformat() for d in dates_used]
        
        distribution[key] = {
            "label": label,
            "count": count,
            "percentage": round((count / total_count * 100.0), 2) if total_count > 0 else 0.0,
            "dates": dates_formatted
        }
        
    return {
        "total_analyzed": total_count,
        "days_window": days,
        "distribution": distribution
    }

def get_editorial_heatmap(days=90):
    """
    Retorna a estrutura simples para renderização de heatmaps de eixos editoriais.
    """
    end_date = timezone.localtime().date()
    start_date = end_date - timedelta(days=days)
    
    reflections = DailyReflection.objects.filter(
        date__range=(start_date, end_date)
    ).exclude(theme_key="")
    
    counts = Counter(reflections.values_list("theme_key", flat=True))
    
    # Inicializa todos os eixos conhecidos com 0 para consistência do mapa
    heatmap = {theme["key"]: 0 for theme in DAILY_REFLECTION_THEMES}
    for key, count in counts.items():
        heatmap[key] = count
        
    return heatmap

def get_emotional_theme_frequency(days=30):
    """
    Agrupa, limpa e ranqueia as tags e termos semânticos gerados pela IA.
    """
    end_date = timezone.localtime().date()
    start_date = end_date - timedelta(days=days)
    
    raw_themes = DailyReflection.objects.filter(
        date__range=(start_date, end_date)
    ).exclude(emotional_theme="").values_list("emotional_theme", flat=True)
    
    all_terms = []
    phrase_counts = Counter()
    
    for entry in raw_themes:
        phrase = entry.strip()
        if phrase:
            phrase_counts[phrase] += 1
            # Quebra por vírgula para extrair termos individuais
            parts = [p.strip().lower() for p in phrase.split(",")]
            for part in parts:
                if part:
                    all_terms.append(part)
                    
    term_counts = Counter(all_terms)
    
    return {
        "days_window": days,
        "phrases_ranking": [{"phrase": k, "count": v} for k, v in phrase_counts.most_common(10)],
        "individual_terms_ranking": [{"term": k, "count": v} for k, v in term_counts.most_common(15)]
    }

def get_scripture_coverage(days=90):
    """
    Analisa a cobertura e a diversidade canônica das passagens bíblicas utilizadas.
    """
    end_date = timezone.localtime().date()
    start_date = end_date - timedelta(days=days)
    
    reflections = DailyReflection.objects.filter(
        date__range=(start_date, end_date)
    ).select_related("passage")
    
    total = reflections.count()
    if total == 0:
        return {
            "total_analyzed": 0,
            "book_frequency": {},
            "salms_percentage": 0.0,
            "ot_percentage": 0.0,
            "nt_percentage": 0.0,
            "ranking": []
        }
        
    books = []
    chapters = []
    salms_count = 0
    nt_count = 0
    ranking = []
    
    for r in reflections:
        ref_str = r.scripture_reference
        ranking.append({
            "date": r.date.isoformat(),
            "reference": ref_str,
            "title": r.title
        })
        
        # Tenta extrair dados estruturados através da ForeignKey com BiblePassage
        if r.passage:
            book_name = r.passage.book_name
            chap = r.passage.chapter
        else:
            # Fallback robusto por regex caso a ForeignKey esteja nula ou órfã
            match = re.match(r"^([\d\s\w]+?)\s+(\d+)", ref_str.strip())
            if match:
                book_name = match.group(1).strip()
                chap = match.group(2).strip()
            else:
                book_name = "Desconhecido"
                chap = "1"
                
        cleaned_book = book_name.strip()
        books.append(cleaned_book)
        chapters.append(f"{cleaned_book} {chap}")
        
        normalized_book = cleaned_book.lower()
        if "salmo" in normalized_book or "salmo" in normalized_book:
            salms_count += 1
            
        if normalized_book in NT_BOOKS or any(nt in normalized_book for nt in ["mateus", "marcos", "lucas", "joão", "joao", "atos", "romanos", "coríntios", "corintios", "gálatas", "galatas", "efésios", "efesios", "filipenses", "colossenses", "tessalonicenses", "timóteo", "timoteo", "tito", "filemom", "hebreus", "tiago", "pedro", "judas", "apocalipse"]):
            nt_count += 1
            
    book_counts = Counter(books)
    chapter_counts = Counter(chapters)
    
    # Livros ausentes (auditoria de desertos editoriais)
    all_themes_hints = []
    for t in DAILY_REFLECTION_THEMES:
        for hint in t.get("scripture_hints", []):
            m = re.match(r"^([\d\s\w]+?)\s+(\d+)", hint)
            if m:
                all_themes_hints.append(m.group(1).strip())
    unique_hints_books = set(all_themes_hints)
    absent_books = list(unique_hints_books - set(book_counts.keys()))
    
    return {
        "total_analyzed": total,
        "days_window": days,
        "book_frequency": dict(book_counts),
        "chapter_frequency": dict(chapter_counts.most_common(10)),
        "salms_percentage": round((salms_count / total * 100.0), 2),
        "nt_percentage": round((nt_count / total * 100.0), 2),
        "ot_percentage": round(((total - nt_count) / total * 100.0), 2),
        "absent_books_from_hints": absent_books,
        "ranking": ranking[:15]
    }

def detect_psalms_dominance(days=90):
    """
    Retorna True e métricas se a dominância de Salmos for excessiva (> 40%).
    """
    coverage = get_scripture_coverage(days)
    percentage = coverage.get("salms_percentage", 0.0)
    
    return {
        "is_dominant": percentage > 40.0,
        "percentage": percentage,
        "total_analyzed": coverage.get("total_analyzed", 0)
    }

def get_saturation_alerts(days=14):
    """
    Varre o histórico para detectar saturações, repetições de eixos,
    livros bíblicos ou proximidade semântica (Jaccard) de share_quotes.
    """
    end_date = timezone.localtime().date()
    start_date = end_date - timedelta(days=days)
    
    reflections = DailyReflection.objects.filter(
        date__range=(start_date, end_date)
    ).select_related("passage").order_by("-date")
    
    total = reflections.count()
    alerts = []
    
    if total == 0:
        return alerts
        
    # 1. Alerta de Repetição de Eixos (Theme Key)
    theme_keys = list(reflections.values_list("theme_key", flat=True))
    theme_counts = Counter(theme_keys)
    for key, count in theme_counts.items():
        if count > 4:
            theme_meta = next((t for t in DAILY_REFLECTION_THEMES if t["key"] == key), None)
            label = theme_meta["label"] if theme_meta else key.capitalize()
            alerts.append({
                "level": "warning",
                "category": "theme_saturation",
                "message": f"O eixo '{label}' está saturado: apareceu {count} vezes nos últimos {days} dias."
            })
            
    # 2. Alerta de Concentração Bíblica (Livros)
    books = []
    for r in reflections:
        if r.passage:
            books.append(r.passage.book_name)
        else:
            match = re.match(r"^([\d\s\w]+?)\s+(\d+)", r.scripture_reference)
            if match:
                books.append(match.group(1).strip())
                
    book_counts = Counter(books)
    for book, count in book_counts.items():
        if count > 3:
            alerts.append({
                "level": "warning",
                "category": "scripture_saturation",
                "message": f"Alta concentração de leitura: o livro de '{book}' foi usado {count} vezes nos últimos {days} dias."
            })
            
    # 3. Alerta de Similaridade Semântica em Share Quotes
    ref_list = list(reflections)
    for i in range(len(ref_list)):
        for j in range(i + 1, len(ref_list)):
            q1 = ref_list[i].share_quote
            q2 = ref_list[j].share_quote
            similarity = _calculate_jaccard_similarity(q1, q2)
            
            if similarity > 0.4:
                alerts.append({
                    "level": "danger",
                    "category": "semantic_similarity",
                    "message": (
                        f"Detecção de fadiga semântica: os fragmentos (share_quotes) de "
                        f"{ref_list[i].date.isoformat()} e {ref_list[j].date.isoformat()} possuem "
                        f"{round(similarity * 100.0, 1)}% de similaridade vocabular."
                    ),
                    "metadata": {
                        "date_a": ref_list[i].date.isoformat(),
                        "quote_a": q1,
                        "date_b": ref_list[j].date.isoformat(),
                        "quote_b": q2,
                        "similarity_score": similarity
                    }
                })
                
    return alerts

def get_editorial_timeline(days=30):
    """
    Retorna a jornada sequencial das reflexões diárias geradas.
    """
    end_date = timezone.localtime().date()
    start_date = end_date - timedelta(days=days)
    
    reflections = DailyReflection.objects.filter(
        date__range=(start_date, end_date)
    ).order_by("-date")
    
    timeline = []
    for r in reflections:
        theme_meta = next((t for t in DAILY_REFLECTION_THEMES if t["key"] == r.theme_key), None)
        theme_label = theme_meta["label"] if theme_meta else r.theme_key.capitalize()
        
        timeline.append({
            "date": r.date.isoformat(),
            "theme_key": r.theme_key,
            "theme_label": theme_label,
            "emotional_theme": r.emotional_theme,
            "scripture_reference": r.scripture_reference,
            "title": r.title,
            "share_quote": r.share_quote
        })
        
    return timeline

def generate_editorial_report(days=30):
    """
    Produz um relatório textual consolidado e humanizado (painel curatorial) em português.
    """
    timeline = get_editorial_timeline(days)
    coverage = get_scripture_coverage(days)
    alerts = get_saturation_alerts(days)
    dist = get_theme_distribution(days)
    
    total = len(timeline)
    if total == 0:
        return (
            "### Relatório Curatorial CAPIO\n"
            "Não foram encontradas reflexões diárias gravadas no período especificado.\n"
            "Gere reflexões no sistema para ativar a inteligência semântica."
        )
        
    # Identifica eixos ausentes
    keys_used = set(r["theme_key"] for r in timeline)
    all_keys = set(t["key"] for t in DAILY_REFLECTION_THEMES)
    absent_keys = all_keys - keys_used
    
    absent_labels = []
    for ak in absent_keys:
        meta = next((t for t in DAILY_REFLECTION_THEMES if t["key"] == ak), None)
        if meta:
            absent_labels.append(meta["label"])
            
    # Coleta eixos mais e menos frequentes
    most_common_theme = ""
    most_common_count = 0
    if dist["distribution"]:
        sorted_dist = sorted(dist["distribution"].items(), key=lambda item: item[1]["count"], reverse=True)
        most_common_theme = sorted_dist[0][1]["label"]
        most_common_count = sorted_dist[0][1]["count"]
        
    # Montagem do relatório elegante
    report = (
        f"### CAPIO — Painel Curatorial Inteligente ({timezone.now().strftime('%d/%m/%Y %H:%M')})\n\n"
        f"**1. RESUMO DA JORNADA ESPIRITUAL**\n"
        f"* **Período Analisado**: Últimos {days} dias.\n"
        f"* **Reflexões Auditadas**: {total} meditações diárias.\n"
        f"* **Eixo Dominante**: *{most_common_theme}* ({most_common_count} ocorrências).\n"
        f"* **Cobertura Bíblica**: {coverage.get('salms_percentage', 0.0)}% Salmos | {coverage.get('nt_percentage', 0.0)}% Novo Testamento | {coverage.get('ot_percentage', 0.0)}% Antigo Testamento.\n\n"
        f"**2. DESERTOS EDITORIAIS (EIXOS AUSENTES)**\n"
    )
    
    if absent_labels:
        report += "Os seguintes temas espirituais não foram apresentados ao leitor neste período e precisam ser resgatados:\n"
        for label in absent_labels:
            report += f"  - *{label}*\n"
    else:
        report += "Todos os 14 eixos editoriais da CAPIO foram representados com equilíbrio nas últimas leituras!\n"
        
    report += "\n**3. ALERTAS DE SATURAÇÃO E FADIGA SEMÂNTICA**\n"
    if alerts:
        for a in alerts:
            lvl = "[AVISO]" if a["level"] == "warning" else "[CRÍTICO]"
            report += f"  - {lvl} {a['message']}\n"
    else:
        report += "Nenhum vício de repetição, fadiga semântica de fragmentos ou saturação de livros bíblicos foi identificado. A plataforma respira com amplitude saudável.\n"
        
    report += (
        "\n**4. DIRETRIZ E RECOMENDAÇÃO CURATORIAL**\n"
        "Com base no padrão semântico auditado, a recomendação para o próximo ciclo de curadoria é: "
    )
    
    if absent_keys:
        report += (
            f"Priorizar o resgate do eixo *{absent_labels[0]}* nas próximas reflexões. "
            f"Evitar alta concentração de passagens de *{coverage.get('chapter_frequency', {}).get('Salmos', 'Salmos')}* "
            f"para manter a diversidade canônica saudável."
        )
    else:
        report += "Manter a rotação determinística atual ativa e auditar novamente em 15 dias."
        
    return report
