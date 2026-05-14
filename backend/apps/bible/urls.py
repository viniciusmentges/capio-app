from django.urls import path
from .views import ExplainView, HistoryView, PublicExplanationDetailView

urlpatterns = [
    path('explain/', ExplainView.as_view(), name='explain'),
    path('history/', HistoryView.as_view(), name='history'),
    path('public/<int:pk>/', PublicExplanationDetailView.as_view(), name='public-detail'),
]

