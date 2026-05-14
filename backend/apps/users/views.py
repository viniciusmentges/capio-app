from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from .serializers import UserSerializer, RegisterSerializer, FeedbackSerializer
from services.feedback.feedback_service import FeedbackService
from services.exceptions import ContentBlockedException, NotFoundException

class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

class MeView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

class FeedbackView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = FeedbackSerializer(data=request.data)
        if serializer.is_valid():
            try:
                res = FeedbackService.submit(
                    user=request.user,
                    response_type=serializer.validated_data['response_type'],
                    content_ref_id=serializer.validated_data['content_ref_id'],
                    helpful=serializer.validated_data['helpful'],
                    comment=serializer.validated_data.get('comment', '')
                )
                return Response(res, status=status.HTTP_201_CREATED)
            except NotFoundException as e:
                return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
            except Exception as e:
                return Response({"error": "Internal server error."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
