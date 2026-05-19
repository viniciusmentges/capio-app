from services.exceptions import NotFoundException
import hashlib
import random
import logging
from typing import Dict, Any
from django.db import transaction
from django.db.models import Max, Q
from apps.devotional.models import Emotion, DevotionalContent, UserDevotional
from apps.ai_core.models import AIRequest, GeneratedResponse
from services.ai import get_ai_service
from apps.bible.models import BiblePassage

logger = logging.getLogger(__name__)

# Pool controlado e curado de passagens bíblicas para assegurar a filosofia "Scripture First"
EMOTION_SCRIPTURES = {
    "ansioso": [
        {"canonical_id": "PHP.4.6-7", "book_name": "Filipenses", "chapter": 4, "verses": "6-7", "text_original": "Não andem ansiosos por coisa alguma, mas em tudo, pela oração e súplicas, e com ação de graças, apresentem seus pedidos a Deus. E a paz de Deus, que excede todo o entendimento, guardará o seu coração e a sua mente em Cristo Jesus.", "reference_display": "Filipenses 4:6-7"},
        {"canonical_id": "1PE.5.7", "book_name": "1 Pedro", "chapter": 5, "verses": "7", "text_original": "Lancem sobre ele toda a sua ansiedade, porque ele tem cuidado de vocês.", "reference_display": "1 Pedro 5:7"},
        {"canonical_id": "PSA.94.19", "book_name": "Salmos", "chapter": 94, "verses": "19", "text_original": "Quando a ansiedade já dominava o meu íntimo, o teu consolo trouxe alívio à minha alma.", "reference_display": "Salmos 94:19"},
    ],
    "triste": [
        {"canonical_id": "PSA.34.18", "book_name": "Salmos", "chapter": 34, "verses": "18", "text_original": "O Senhor está perto dos que têm o coração quebrantado e salva os de espírito abatido.", "reference_display": "Salmos 34:18"},
        {"canonical_id": "MAT.5.4", "book_name": "Mateus", "chapter": 5, "verses": "4", "text_original": "Bem-aventurados os que choram, pois serão consolados.", "reference_display": "Mateus 5:4"},
        {"canonical_id": "REV.21.4", "book_name": "Apocalipse", "chapter": 21, "verses": "4", "text_original": "Ele enxugará dos seus olhos toda lágrima. Não haverá mais morte, nem tristeza, nem choro, nem dor, pois a antiga ordem já passou.", "reference_display": "Apocalipse 21:4"},
    ],
    "medo": [
        {"canonical_id": "ISA.41.10", "book_name": "Isaías", "chapter": 41, "verses": "10", "text_original": "Por isso não tema, pois estou com você; não se alinhe, pois sou o seu Deus. Eu o fortalecerei e o ajudarei; eu o segurarei com a minha mão direita vitoriosa.", "reference_display": "Isaías 41:10"},
        {"canonical_id": "PSA.56.3", "book_name": "Salmos", "chapter": 56, "verses": "3", "text_original": "Mas, no dia em que eu temer, hei de confiar em ti.", "reference_display": "Salmos 56:3"},
        {"canonical_id": "2TI.1.7", "book_name": "2 Timóteo", "chapter": 1, "verses": "7", "text_original": "Pois Deus não nos deu espírito de covardia, mas de poder, de amor e de equilíbrio.", "reference_display": "2 Timóteo 1:7"},
    ],
    "desmotivado": [
        {"canonical_id": "ISA.40.31", "book_name": "Isaías", "chapter": 40, "verses": "31", "text_original": "Mas aqueles que esperam no Senhor renovam as suas forças. Voam bem alto como águias; correm e não ficam exaustos, andam e não se cansam.", "reference_display": "Isaías 40:31"},
        {"canonical_id": "GAL.6.9", "book_name": "Gálatas", "chapter": 6, "verses": "9", "text_original": "E não nos cansemos de fazer o bem, pois no tempo próprio colheremos, se não desanimarmos.", "reference_display": "Gálatas 6:9"},
        {"canonical_id": "JOS.1.9", "book_name": "Josué", "chapter": 1, "verses": "9", "text_original": "Não fui eu que ordenei a você? Seja forte e corajoso! Não se apavore nem desanime, pois o Senhor, o seu Deus, estará com você por onde você andar.", "reference_display": "Josué 1:9"},
    ],
    "sozinho": [
        {"canonical_id": "MAT.28.20", "book_name": "Mateus", "chapter": 28, "verses": "20", "text_original": "E lembrem-se: eu estarei sempre com vocês, até o fim dos tempos.", "reference_display": "Mateus 28:20"},
        {"canonical_id": "PSA.23.4", "book_name": "Salmos", "chapter": 23, "verses": "4", "text_original": "Mesmo que eu ande pelo vale da sombra da morte, não temerei mal algum, porque tu estás comigo; a tua vara e o teu cajado me consolam.", "reference_display": "Salmos 23:4"},
        {"canonical_id": "HEB.13.5", "book_name": "Hebreus", "chapter": 13, "verses": "5", "text_original": "Porque Deus mesmo disse: 'Nunca o deixarei, nunca o abandonarei'.", "reference_display": "Hebreus 13:5"},
    ],
    "sem-esperanca": [
        {"canonical_id": "JER.29.11", "book_name": "Jeremias", "chapter": 29, "verses": "11", "text_original": "Porque sou eu que conheço os planos que tenho para vocês', diz o Senhor, 'planos de fazê-los prosperar e não de causar dano, planos de dar a vocês esperança e um futuro.", "reference_display": "Jeremias 29:11"},
        {"canonical_id": "ROM.15.13", "book_name": "Romanos", "chapter": 15, "verses": "13", "text_original": "Que o Deus da esperança os encha de toda alegria e paz, por sua confiança nele, para que vocês transbordem de esperança pelo poder do Espírito Santo.", "reference_display": "Romanos 15:13"},
        {"canonical_id": "PSA.42.11", "book_name": "Salmos", "chapter": 42, "verses": "11", "text_original": "Por que você está assim tão abatida, ó minha alma? Por que se perturba dentro de mim? Deposite a sua esperança em Deus, pois ainda o louvarei; ele é o meu Salvador e o meu Deus.", "reference_display": "Salmos 42:11"},
    ],
    "sem_esperanca": [
        {"canonical_id": "JER.29.11", "book_name": "Jeremias", "chapter": 29, "verses": "11", "text_original": "Porque sou eu que conheço os planos que tenho para vocês', diz o Senhor, 'planos de fazê-los prosperar e não de causar dano, planos de dar a vocês esperança e um futuro.", "reference_display": "Jeremias 29:11"},
        {"canonical_id": "ROM.15.13", "book_name": "Romanos", "chapter": 15, "verses": "13", "text_original": "Que o Deus da esperança os encha de toda alegria e paz, por sua confiança nele, para que vocês transbordem de esperança pelo poder do Espírito Santo.", "reference_display": "Romanos 15:13"},
        {"canonical_id": "PSA.42.11", "book_name": "Salmos", "chapter": 42, "verses": "11", "text_original": "Por que você está assim tão abatida, ó minha alma? Por que se perturba dentro de mim? Deposite a sua esperança em Deus, pois ainda o louvarei; ele é o meu Salvador e o meu Deus.", "reference_display": "Salmos 42:11"},
    ],
    "direcao": [
        {"canonical_id": "PRO.3.5-6", "book_name": "Provérbios", "chapter": 3, "verses": "5-6", "text_original": "Confie no Senhor de todo o seu coração e não se apóie em seu próprio entendimento; reconheça o Senhor em todos os seus caminhos, e ele endireitará as suas veredas.", "reference_display": "Provérbios 3:5-6"},
        {"canonical_id": "PSA.119.105", "book_name": "Salmos", "chapter": 119, "verses": "105", "text_original": "A tua palavra é lâmpada que ilumina os meus passos e luz que clareia o meu caminho.", "reference_display": "Salmos 119:105"},
        {"canonical_id": "ISA.30.21", "book_name": "Isaías", "chapter": 30, "verses": "21", "text_original": "Quer você se volte para a direita quer para a esquerda, uma voz atrás de você dirá: 'Este é o caminho; siga-o'.", "reference_display": "Isaías 30:21"},
    ],
    "gratidao": [
        {"canonical_id": "1TH.5.18", "book_name": "1 Tessalonicenses", "chapter": 5, "verses": "18", "text_original": "Deem graças in todas as circunstâncias, pois esta é a vontade de Deus para vocês em Cristo Jesus.", "reference_display": "1 Tessalonicenses 5:18"},
        {"canonical_id": "PSA.100.4", "book_name": "Salmos", "chapter": 100, "verses": "4", "text_original": "Entrem por suas portas com ações de graças e em seus átrios com louvor; deem-lhe graças e bendigam o seu nome.", "reference_display": "Salmos 100:4"},
        {"canonical_id": "COL.3.17", "book_name": "Colossenses", "chapter": 3, "verses": "17", "text_original": "Tudo o que fizerem, seja em palavra seja em ação, façam-no em nome do Senhor Jesus, dando graças por meio dele a Deus Pai.", "reference_display": "Colossenses 3:17"},
    ]
}

class DevotionalService:
    @classmethod
    def get_for_emotion(cls, emotion_slug: str, user) -> Dict[str, Any]:
        emotion = Emotion.objects.filter(slug=emotion_slug).first()
        if not emotion:
            raise NotFoundException(f"Emotion with slug '{emotion_slug}' not found.")

        # 1. Tentar buscar da Biblioteca (Excluindo lidos pelo usuário)
        user_history = UserDevotional.objects.filter(user=user).values_list('content_id', flat=True)
        
        # Seleção por IDs leve: Executa uma query leve que traz apenas IDs cobertos por index.
        # Evita transações de alto OFFSET que exigem varredura sequencial profunda.
        available_ids = list(DevotionalContent.objects.filter(
            emotion=emotion, 
            is_active=True
        ).exclude(id__in=user_history).values_list('id', flat=True))

        if available_ids:
            chosen_id = random.choice(available_ids)
            content = DevotionalContent.objects.get(id=chosen_id)
            
            with transaction.atomic():
                UserDevotional.objects.create(user=user, content=content)
                GeneratedResponse.objects.create(
                    response_type='DEVOTIONAL',
                    user=user,
                    content_ref_id=content.id,
                    filter_status='clean',
                    metadata={"cached": True, "source": "foundation_library", "is_new_for_user": True}
                )
            return {
                "title": content.title,
                "scripture_reference": content.scripture_reference,
                "scripture_text": content.scripture_text,
                "reflection": content.reflection,
                "practical_application": content.practical_application,
                "guiding_question": content.guiding_question,
                "prayer": content.prayer,
                "ai_generated": content.ai_generated,
                "cached": True
            }

        # 1.1 Rotação da Biblioteca (Se o usuário já viu tudo, mas a biblioteca não está vazia)
        any_available_ids = list(DevotionalContent.objects.filter(
            emotion=emotion, 
            is_active=True
        ).values_list('id', flat=True))
        
        if any_available_ids:
            chosen_id = random.choice(any_available_ids)
            content = DevotionalContent.objects.get(id=chosen_id)
            
            with transaction.atomic():
                GeneratedResponse.objects.create(
                    response_type='DEVOTIONAL',
                    user=user,
                    content_ref_id=content.id,
                    filter_status='clean',
                    metadata={"cached": True, "source": "library_rotation", "is_new_for_user": False}
                )
            return {
                "title": content.title,
                "scripture_reference": content.scripture_reference,
                "scripture_text": content.scripture_text,
                "reflection": content.reflection,
                "practical_application": content.practical_application,
                "guiding_question": content.guiding_question,
                "prayer": content.prayer,
                "ai_generated": content.ai_generated,
                "cached": True
            }

        # 2. Se a biblioteca estiver REALMENTE vazia, executamos a Expansão Orgânica.
        slug_key = emotion.slug.replace("-", "_")
        scripture_pool = EMOTION_SCRIPTURES.get(slug_key) or EMOTION_SCRIPTURES["ansioso"]
        scripture_seed = random.choice(scripture_pool)

        with transaction.atomic():
            bible_passage, _ = BiblePassage.objects.get_or_create(
                canonical_id=scripture_seed["canonical_id"],
                defaults={
                    "book_name": scripture_seed["book_name"],
                    "chapter": scripture_seed["chapter"],
                    "verses": scripture_seed["verses"],
                    "text_original": scripture_seed["text_original"],
                    "translation": "NVI",
                    "language": "pt"
                }
            )

        ai_service = get_ai_service()
        input_hash = hashlib.sha256(f"{emotion.slug}:{bible_passage.canonical_id}".encode()).hexdigest()

        ai_request = AIRequest.objects.create(
            request_type='devotional',
            input_hash=input_hash,
            input_data={"emotion_name": emotion.name, "canonical_id": bible_passage.canonical_id},
            status='pending'
        )

        try:
            ai_response = ai_service.devotional_for_emotion(
                emotion_name=emotion.name,
                reference_display=scripture_seed["reference_display"],
                scripture_text=bible_passage.text_original
            )
        except Exception as e:
            logger.error("Falha ao chamar a API de IA no fluxo de devocional: %s", e)
            ai_request.status = 'failed'
            ai_request.output_data = {"error": str(e)}
            ai_request.save()
            raise e

        ai_request.status = 'success'
        ai_request.output_data = ai_response
        ai_request.save()

        # Agrupamento de escritas críticas
        with transaction.atomic():
            content = DevotionalContent.objects.create(
                emotion=emotion,
                passage=bible_passage,
                title=ai_response.get("title", f"O repouso em {emotion.name}"),
                scripture_reference=scripture_seed["reference_display"],
                scripture_text=bible_passage.text_original,
                reflection=ai_response.get("reflection", ""),
                practical_application=ai_response.get("practical_application", ""),
                guiding_question=ai_response.get("guiding_question", ""),
                prayer=ai_response.get("prayer", ""),
                is_active=True,
                ai_generated=ai_response.get("ai_generated", True)
            )

            UserDevotional.objects.create(user=user, content=content)

            GeneratedResponse.objects.create(
                response_type='DEVOTIONAL',
                user=user,
                ai_request=ai_request,
                content_ref_id=content.id,
                filter_status='clean',
                metadata={"cached": False, "source": "editorial_motor", "organic_growth": True}
            )

        return {
            "title": content.title,
            "scripture_reference": content.scripture_reference,
            "scripture_text": content.scripture_text,
            "reflection": content.reflection,
            "practical_application": content.practical_application,
            "guiding_question": content.guiding_question,
            "prayer": content.prayer,
            "ai_generated": content.ai_generated,
            "cached": False
        }
