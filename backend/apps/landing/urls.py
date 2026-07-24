from django.urls import path
from .views import LandingScreenshotListView, LeadCaptureView, BrevoAuditView

urlpatterns = [
    path('landing-screenshots/', LandingScreenshotListView.as_view(), name='landing-screenshots'),
    path('leads/', LeadCaptureView.as_view(), name='lead-capture'),
    path('audit/', BrevoAuditView.as_view(), name='audit-capture'),
]
