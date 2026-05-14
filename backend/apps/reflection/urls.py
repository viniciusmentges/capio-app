from django.urls import path
from .views import TodayView, RespondView, HistoryView, PublicReflectionDetailView

urlpatterns = [
    path('today/', TodayView.as_view(), name='today'),
    path('today/respond/', RespondView.as_view(), name='respond'),
    path('history/', HistoryView.as_view(), name='history'),
    path('public/<int:pk>/', PublicReflectionDetailView.as_view(), name='public-detail'),
]

