from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse  # <-- DODAJ TO

def root(request):
    return JsonResponse({"status": "ok"})

urlpatterns = [
    path("", root),
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]