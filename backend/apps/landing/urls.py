from django.urls import path
from .views import LandingScreenshotListView

urlpatterns = [
    path('landing-screenshots/', LandingScreenshotListView.as_view(), name='landing-screenshots'),
]
