from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Emotion, UserDevotional
from .serializers import EmotionSerializer, DevotionalRequestSerializer, UserDevotionalSerializer
from services.devotional.devotional_service import DevotionalService
from services.exceptions import NotFoundException

class EmotionsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        emotions = Emotion.objects.all()
        serializer = EmotionSerializer(emotions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class DevotionalByEmotionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = DevotionalRequestSerializer(data=request.data)
        if serializer.is_valid():
            try:
                res = DevotionalService.get_for_emotion(
                    emotion_slug=serializer.validated_data['emotion_slug'],
                    user=request.user
                )
                return Response(res, status=status.HTTP_200_OK)
            except NotFoundException as e:
                return Response({"error": "not_found", "message": str(e)}, status=status.HTTP_404_NOT_FOUND)
            except Exception as e:
                return Response({"error": "Internal server error."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class HistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            history = UserDevotional.objects.filter(user=request.user).select_related('content').order_by('-accessed_at')
            serializer = UserDevotionalSerializer(history, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": "Internal server error."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

from .models import DevotionalContent
from .serializers import DevotionalContentSerializer
from rest_framework.permissions import AllowAny

class PublicDevotionalDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, pk):
        try:
            content = DevotionalContent.objects.get(pk=pk)
            serializer = DevotionalContentSerializer(content)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except DevotionalContent.DoesNotExist:
            return Response({"error": "not_found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": "Internal server error."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
