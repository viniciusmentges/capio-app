from django.urls import path
from .views import EmotionsView, DevotionalByEmotionView, HistoryView, PublicDevotionalDetailView

urlpatterns = [
    path('emotions/', EmotionsView.as_view(), name='emotions'),
    path('by-emotion/', DevotionalByEmotionView.as_view(), name='by_emotion'),
    path('history/', HistoryView.as_view(), name='history'),
    path('public/<int:pk>/', PublicDevotionalDetailView.as_view(), name='public-detail'),
]

