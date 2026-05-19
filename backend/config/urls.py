from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from django.db import connection
from django.utils import timezone
from django.conf import settings

def health_check(request):
    db_status = "ok"
    try:
        connection.ensure_connection()
    except Exception as e:
        db_status = f"error"
        
    status = "ok" if db_status == "ok" else "degraded"
    
    return JsonResponse({
        "status": status,
        "database": db_status,
        "timestamp": timezone.now().isoformat(),
        "environment": "production" if not getattr(settings, 'DEBUG', True) else "development"
    }, status=200 if status == "ok" else 503)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/health/', health_check, name='health_check'),
    
    # Apps URLs
    path('api/', include('apps.users.urls')),
    path('api/bible/', include('apps.bible.urls')),
    path('api/devotional/', include('apps.devotional.urls')),
    path('api/reflection/', include('apps.reflection.urls')),
]
