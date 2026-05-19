import logging
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from .serializers import UserSerializer, RegisterSerializer, FeedbackSerializer, PushSubscriptionSerializer
from services.feedback.feedback_service import FeedbackService
from services.exceptions import ContentBlockedException, NotFoundException
from apps.users.models import PushSubscription

logger = logging.getLogger(__name__)

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


class PushSubscriptionView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PushSubscriptionSerializer(data=request.data)
        if serializer.is_valid():
            try:
                endpoint = serializer.validated_data['endpoint']
                p256dh = serializer.validated_data['p256dh']
                auth = serializer.validated_data['auth']
                
                # Novos campos opcionais
                user_agent = serializer.validated_data.get('user_agent')
                platform = serializer.validated_data.get('platform')
                timezone = serializer.validated_data.get('timezone', 'America/Sao_Paulo')
                preferred_time = serializer.validated_data.get('preferred_time', 'morning')
                enabled = serializer.validated_data.get('enabled', True)
                
                # Vincular o usuário se ele estiver autenticado
                user = request.user if request.user.is_authenticated else None
                
                subscription, created = PushSubscription.objects.update_or_create(
                    endpoint=endpoint,
                    defaults={
                        'p256dh': p256dh,
                        'auth': auth,
                        'user': user,
                        'user_agent': user_agent,
                        'platform': platform,
                        'timezone': timezone,
                        'preferred_time': preferred_time,
                        'enabled': enabled
                    }
                )
                
                status_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
                return Response({
                    "message": "Inscrição de notificações push salva com sucesso.",
                    "id": subscription.id,
                    "preferred_time": subscription.preferred_time
                }, status=status_code)
            except Exception as e:
                logger.error("Erro interno ao criar/atualizar assinatura Push: %s", e, exc_info=True)
                return Response(
                    {"error": "Não foi possível registrar a assinatura no momento. Preservando a quietude do espaço."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PushUnsubscribeView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        endpoint = request.data.get('endpoint')
        if not endpoint:
            return Response({"error": "O campo endpoint é obrigatório."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            subscription = PushSubscription.objects.get(endpoint=endpoint)
            subscription.enabled = False
            subscription.save()
            return Response({"message": "Inscrição de notificações push desativada com sucesso."}, status=status.HTTP_200_OK)
        except PushSubscription.DoesNotExist:
            return Response({"error": "Inscrição não encontrada."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error("Erro interno ao cancelar assinatura Push: %s", e, exc_info=True)
            return Response(
                {"error": "Não foi possível desativar a assinatura no momento. Preservando a quietude do espaço."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class PushPreferencesView(APIView):
    permission_classes = [AllowAny]

    def patch(self, request):
        endpoint = request.data.get('endpoint')
        if not endpoint:
            return Response({"error": "O campo endpoint é obrigatório."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            subscription = PushSubscription.objects.get(endpoint=endpoint)
            
            # Atualizar apenas preferências permitidas
            if 'preferred_time' in request.data:
                subscription.preferred_time = request.data['preferred_time']
            if 'timezone' in request.data:
                subscription.timezone = request.data['timezone']
            if 'enabled' in request.data:
                subscription.enabled = request.data['enabled']
                
            subscription.save()
            
            return Response({
                "message": "Preferências de notificações push atualizadas com sucesso.",
                "preferred_time": subscription.preferred_time,
                "enabled": subscription.enabled
            }, status=status.HTTP_200_OK)
        except PushSubscription.DoesNotExist:
            return Response({"error": "Inscrição não encontrada."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error("Erro interno ao atualizar preferências de Push: %s", e, exc_info=True)
            return Response(
                {"error": "Não foi possível atualizar as preferências no momento. Preservando a quietude do espaço."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
