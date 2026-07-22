from django.urls import path
from .views import LandingScreenshotListView, LeadCaptureView

urlpatterns = [
    path('landing-screenshots/', LandingScreenshotListView.as_view(), name='landing-screenshots'),
    path('leads/', LeadCaptureView.as_view(), name='lead-capture'),
]
