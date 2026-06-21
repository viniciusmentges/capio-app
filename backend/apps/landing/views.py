from rest_framework import generics
from rest_framework.permissions import AllowAny
from .models import LandingScreenshot
from .serializers import LandingScreenshotSerializer

class LandingScreenshotListView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = LandingScreenshotSerializer
    pagination_class = None  # Não queremos paginação, queremos a lista completa

    def get_queryset(self):
        return LandingScreenshot.objects.filter(is_active=True).order_by('sort_order', 'id')
