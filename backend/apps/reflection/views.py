from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import UserReflectionResponse
from .serializers import RespondRequestSerializer, UserReflectionResponseSerializer
from services.reflection.reflection_service import ReflectionService
from services.exceptions import NotFoundException

class TodayView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            res = ReflectionService.get_today(request.user)
            return Response(res, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": "Internal server error."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class RespondView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = RespondRequestSerializer(data=request.data)
        if serializer.is_valid():
            try:
                # To save response, we need the reflection id.
                # get_today ensures we have today's reflection created.
                today_res = ReflectionService.get_today(request.user)
                reflection_id = today_res['reflection']['id']

                ReflectionService.save_response(
                    user=request.user,
                    reflection_id=reflection_id,
                    response_text=serializer.validated_data['response_text']
                )
                return Response({"status": "success"}, status=status.HTTP_201_CREATED)
            except NotFoundException as e:
                return Response({"error": "not_found", "message": str(e)}, status=status.HTTP_404_NOT_FOUND)
            except Exception as e:
                return Response({"error": "Internal server error."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class HistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            responses = UserReflectionResponse.objects.filter(user=request.user).select_related('reflection').order_by('-created_at')
            serializer = UserReflectionResponseSerializer(responses, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": "Internal server error."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

from .models import DailyReflection
from .serializers import DailyReflectionSerializer
from rest_framework.permissions import AllowAny

class PublicReflectionDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, pk):
        try:
            reflection = DailyReflection.objects.get(pk=pk)
            serializer = DailyReflectionSerializer(reflection)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except DailyReflection.DoesNotExist:
            return Response({"error": "not_found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": "Internal server error."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
