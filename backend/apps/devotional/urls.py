from django.urls import path
from .views import EmotionsView, DevotionalByEmotionView, HistoryView, PublicDevotionalDetailView, EditorialDevotionalGenerateView

urlpatterns = [
    path('emotions/', EmotionsView.as_view(), name='emotions'),
    path('by-emotion/', DevotionalByEmotionView.as_view(), name='by_emotion'),
    path('history/', HistoryView.as_view(), name='history'),
    path('public/<uuid:public_id>/', PublicDevotionalDetailView.as_view(), name='public-detail'),
    path('editorial/generate/', EditorialDevotionalGenerateView.as_view(), name='editorial-generate'),
]

