from django.urls import path
from .views import (
    ClientListCreateView, ClientDetailView,
    FiscalDeviceListCreateView, FiscalDeviceDetailView,
    ServiceRecordListCreateView,
    RegisterView
)
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    # Endpointy do autentykacji
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'), # Logowanie
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'), # Odświeżanie tokenu

    # Endpointy dla Klientów (CRUD)
    path('clients/', ClientListCreateView.as_view(), name='client-list-create'),
    path('clients/<int:pk>/', ClientDetailView.as_view(), name='client-detail'),

    # Endpointy dla Urządzeń Fiskalnych (CRUD)
    path('devices/', FiscalDeviceListCreateView.as_view(), name='device-list-create'),
    path('devices/<int:pk>/', FiscalDeviceDetailView.as_view(), name='device-detail'),

    # Endpoint dla historii serwisowej (zagnieżdżony pod urządzeniem)
    path('devices/<int:device_pk>/history/', ServiceRecordListCreateView.as_view(), name='service-record-list-create'),
]