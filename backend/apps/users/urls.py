from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import RegisterView, MeView, FeedbackView, PushSubscriptionView, PushUnsubscribeView, PushPreferencesView

urlpatterns = [
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', TokenObtainPairView.as_view(), name='login'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='refresh'),
    path('auth/me/', MeView.as_view(), name='me'),
    path('auth/push/subscribe/', PushSubscriptionView.as_view(), name='push-subscribe'),
    path('auth/push/unsubscribe/', PushUnsubscribeView.as_view(), name='push-unsubscribe'),
    path('auth/push/preferences/', PushPreferencesView.as_view(), name='push-preferences'),
    path('feedback/', FeedbackView.as_view(), name='feedback'),
]
