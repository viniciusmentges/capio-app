import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.reflection.views import SpiritualJourneyView
from rest_framework.test import APIRequestFactory
from rest_framework.request import Request

User = get_user_model()
factory = APIRequestFactory()
view = SpiritualJourneyView()

errors = 0
for user in User.objects.all():
    request = factory.get('/api/reflection/spiritual-journey/')
    request.user = user
    drf_request = Request(request)
    
    response = view.get(drf_request)
    if response.status_code == 500:
        print(f"User {user.id} {user.username} got 500: {response.data}")
        errors += 1

print(f"Total 500 errors: {errors}")
