from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from apps.ai_core.models import GeneratedResponse
from .models import PassageExplanation
from .serializers import ExplainRequestSerializer, PassageExplanationSerializer
from services.bible.explanation_service import BibleService
from services.exceptions import ContentBlockedException

class ExplainView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ExplainRequestSerializer(data=request.data)
        if serializer.is_valid():
            try:
                res = BibleService.explain(
                    reference=serializer.validated_data['reference'],
                    user=request.user
                )
                return Response(res, status=status.HTTP_200_OK)
            except ContentBlockedException as e:
                return Response({"error": "content_blocked", "category": e.category, "message": str(e)}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
            except Exception as e:
                return Response({"error": "Internal server error."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class HistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            # Pegamos os GeneratedResponses do tipo BIBLE para o usuario e trazemos os Passages
            responses = GeneratedResponse.objects.filter(user=request.user, response_type='BIBLE').order_by('-created_at')
            passage_ids = [r.content_ref_id for r in responses]
            passages = PassageExplanation.objects.filter(id__in=passage_ids)
            serializer = PassageExplanationSerializer(passages, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": "Internal server error."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

from .models import PassageExplanation
from .serializers import PassageExplanationSerializer
from rest_framework.permissions import AllowAny

class PublicExplanationDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, pk):
        try:
            explanation = PassageExplanation.objects.get(pk=pk)
            serializer = PassageExplanationSerializer(explanation)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except PassageExplanation.DoesNotExist:
            return Response({"error": "not_found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": "Internal server error."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
