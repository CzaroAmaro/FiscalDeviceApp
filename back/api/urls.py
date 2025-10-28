# urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

# Importujemy cały moduł views, aby łatwiej zarządzać ścieżkami
from . import views

# 1. Tworzymy instancję routera
router = DefaultRouter()

# 2. Rejestrujemy nasze ViewSety w routerze. Router sam stworzy dla nich URL-e.
router.register(r'clients', views.ClientViewSet, basename='client')
router.register(r'manufacturers', views.ManufacturerViewSet, basename='manufacturer')
router.register(r'devices', views.FiscalDeviceViewSet, basename='device')
router.register(r'tickets', views.ServiceTicketViewSet, basename='ticket')
router.register(r'certifications', views.CertificationViewSet, basename='certification')

# 3. Definiujemy główne ścieżki URL
urlpatterns = [
    # Ścieżki autentykacji
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Ścieżki niestandardowe (niepasujące do modelu CRUD)
    path('company-data/<str:nip>/', views.fetch_company_data, name='fetch-company-data'),
    path('technicians/', views.TechnicianListView.as_view(), name='technician-list'),

    # Dołączamy wszystkie ścieżki wygenerowane automatycznie przez router
    path('', include(router.urls)),
]