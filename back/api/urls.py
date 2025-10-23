from django.urls import path
from .views import (
    ClientListCreateView, ClientDetailView,
    FiscalDeviceListCreateView, FiscalDeviceDetailView,
    RegisterView, FetchCompanyDataView,
    ManufacturerListCreateView,
    TechnicianListView,
    CertificationListCreateView,
    ServiceTicketListCreateView,
    ServiceTicketDetailView,
)
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    # Autentykacja
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Pomocniczy endpoint
    path('company-data/<str:nip>/', FetchCompanyDataView.as_view(), name='fetch-company-data'),

    # Klienci
    path('clients/', ClientListCreateView.as_view(), name='client-list-create'),
    path('clients/<int:pk>/', ClientDetailView.as_view(), name='client-detail'),

    # Urządzenia Fiskalne
    path('devices/', FiscalDeviceListCreateView.as_view(), name='device-list-create'),
    path('devices/<int:pk>/', FiscalDeviceDetailView.as_view(), name='device-detail'),

    # --- NOWE ENDPOINTY ---

    # Producenci (słownik)
    path('manufacturers/', ManufacturerListCreateView.as_view(), name='manufacturer-list-create'),

    # Serwisanci (tylko lista)
    path('technicians/', TechnicianListView.as_view(), name='technician-list'),

    # Certyfikaty
    path('certifications/', CertificationListCreateView.as_view(), name='certification-list-create'),

    # Zgłoszenia Serwisowe (CRUD)
    path('tickets/', ServiceTicketListCreateView.as_view(), name='ticket-list-create'),
    path('tickets/<int:pk>/', ServiceTicketDetailView.as_view(), name='ticket-detail'),
]