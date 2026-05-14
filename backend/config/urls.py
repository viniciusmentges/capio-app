from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse

def health_check(request):
    return JsonResponse({"status": "ok"})

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/health/', health_check, name='health_check'),
    
    # Apps URLs
    path('api/', include('apps.users.urls')),
    path('api/bible/', include('apps.bible.urls')),
    path('api/devotional/', include('apps.devotional.urls')),
    path('api/reflection/', include('apps.reflection.urls')),
]
