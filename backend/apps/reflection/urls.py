from django.urls import path
from .views import (
    TodayView, RespondView, HistoryView, PublicReflectionDetailView, 
    EditorialInsightsView, NightView, LiturgicalArchiveView, SpiritualJourneyView
)

urlpatterns = [
    path('today/', TodayView.as_view(), name='today'),
    path('today/respond/', RespondView.as_view(), name='respond'),
    path('history/', HistoryView.as_view(), name='history'),
    path('public/<str:identifier>/', PublicReflectionDetailView.as_view(), name='public-detail'),
    path('archive/<str:identifier>/', PublicReflectionDetailView.as_view(), name='archive-detail'),
    path('editorial-insights/', EditorialInsightsView.as_view(), name='editorial-insights'),
    path('night/', NightView.as_view(), name='night'),
    path('liturgical-archive/', LiturgicalArchiveView.as_view(), name='liturgical-archive'),
    path('spiritual-journey/', SpiritualJourneyView.as_view(), name='spiritual-journey'),
]


