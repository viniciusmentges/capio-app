from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .models import LandingScreenshot, Lead
from .serializers import LandingScreenshotSerializer, LeadSerializer
import os
import requests

class LandingScreenshotListView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = LandingScreenshotSerializer
    pagination_class = None

    def get_queryset(self):
        return LandingScreenshot.objects.filter(is_active=True).order_by('sort_order', 'id')

class LeadCaptureView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = LeadSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        
        email = request.data.get('email')
        if not email:
            return Response({"email": ["Este campo é obrigatório."]}, status=status.HTTP_400_BAD_REQUEST)

        # Trata contato existente ou cria novo
        lead, created = Lead.objects.update_or_create(
            email=email,
            defaults={
                'name': request.data.get('name', ''),
                'consent_given': str(request.data.get('consent_communications')).lower() == 'true',
                'source': request.data.get('source', 'Tudo Parece Pesado'),
                'utm_source': request.data.get('utm_source', ''),
                'utm_medium': request.data.get('utm_medium', ''),
                'utm_campaign': request.data.get('utm_campaign', ''),
                'utm_content': request.data.get('utm_content', ''),
                'utm_term': request.data.get('utm_term', ''),
            }
        )

        if not lead.consent_given:
             return Response({"consent_communications": ["O consentimento é obrigatório."]}, status=status.HTTP_400_BAD_REQUEST)

        self.sync_with_brevo(lead)

        return Response({
            "message": "Você já faz parte deste encontro. Enviamos novamente a obra para o seu e-mail." if not created else "A obra já está a caminho do seu e-mail.",
            "is_new": created
        }, status=status.HTTP_200_OK)

    def sync_with_brevo(self, lead):
        api_key = os.environ.get('BREVO_API_KEY')
        list_id = os.environ.get('BREVO_LIST_ID_PRIMEIRO_ENCONTRO')
        
        if not api_key or not list_id:
            return

        url = "https://api.brevo.com/v3/contacts"
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "api-key": api_key
        }
        
        payload = {
            "email": lead.email,
            "listIds": [int(list_id)],
            "updateEnabled": True
        }

        try:
            response = requests.post(url, json=payload, headers=headers)
            if response.status_code in [201, 204]:
                lead.brevo_sync_status = True
                lead.save(update_fields=['brevo_sync_status'])
            else:
                print(f"Brevo API Error ({response.status_code}): {response.text}")
        except Exception as e:
            print(f"Brevo Request Exception: {str(e)}")
class BrevoAuditView(generics.GenericAPIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        api_key = os.environ.get('BREVO_API_KEY')
        list_id = os.environ.get('BREVO_LIST_ID_PRIMEIRO_ENCONTRO')
        
        audit_result = {
            'env': {
                'has_api_key': bool(api_key),
                'list_id_raw': list_id,
            },
            'test': None
        }
        
        if not api_key or not list_id:
            return Response(audit_result, status=200)
            
        try:
            list_id_int = int(list_id)
            audit_result['env']['list_id_is_int'] = True
        except ValueError:
            audit_result['env']['list_id_is_int'] = False
            return Response(audit_result, status=200)
            
        # Test request
        url = "https://api.brevo.com/v3/contacts"
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "api-key": api_key
        }
        payload = {
            "email": "audit_capio_test@example.com",
            "listIds": [list_id_int],
            "updateEnabled": True
        }
        
        try:
            res = requests.post(url, json=payload, headers=headers)
            audit_result['test'] = {
                'status_code': res.status_code,
                'response': res.text
            }
            # Clean up if created
            if res.status_code in [201, 204]:
                requests.delete(f"{url}/audit_capio_test@example.com", headers=headers)
        except Exception as e:
            audit_result['test'] = {
                'error': str(e)
            }
            
        return Response(audit_result, status=200)
