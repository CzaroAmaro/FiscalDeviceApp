# views.py
import requests
from datetime import date

from rest_framework import viewsets, status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from .models import (
    Client, FiscalDevice, ServiceTicket, Manufacturer, Technician, Certification
)
from .serializers import (
    ClientSerializer,
    FiscalDeviceSerializer, FiscalDeviceWriteSerializer,
    ServiceTicketSerializer, ServiceTicketWriteSerializer,
    RegisterSerializer,
    ManufacturerSerializer,
    TechnicianSerializer,
    CertificationSerializer
)


# --- Widoki oparte na ViewSetach (nowoczesne i zgodne z DRY) ---

class ClientViewSet(viewsets.ModelViewSet):
    """ViewSet do zarządzania klientami (CRUD)."""
    queryset = Client.objects.all().order_by('name')
    serializer_class = ClientSerializer
    permission_classes = [permissions.IsAuthenticated]


class ManufacturerViewSet(viewsets.ModelViewSet):
    """ViewSet do zarządzania producentami (CRUD)."""
    queryset = Manufacturer.objects.all().order_by('name')
    serializer_class = ManufacturerSerializer
    permission_classes = [permissions.IsAuthenticated]


class FiscalDeviceViewSet(viewsets.ModelViewSet):
    """
    ViewSet do zarządzania urządzeniami.
    - Używa różnych serializerów do odczytu i zapisu.
    - Optymalizuje zapytania do bazy danych.
    """
    permission_classes = [permissions.IsAuthenticated]
    queryset = FiscalDevice.objects.select_related('owner', 'brand').all()

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return FiscalDeviceWriteSerializer
        return FiscalDeviceSerializer


class ServiceTicketViewSet(viewsets.ModelViewSet):
    """
    ViewSet do zarządzania zgłoszeniami serwisowymi.
    - Używa różnych serializerów do odczytu i zapisu.
    - Optymalizuje zapytania do bazy danych.
    """
    permission_classes = [permissions.IsAuthenticated]
    queryset = ServiceTicket.objects.select_related(
        'client', 'device__brand', 'assigned_technician__user'
    ).all()

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return ServiceTicketWriteSerializer
        return ServiceTicketSerializer


class CertificationViewSet(viewsets.ModelViewSet):
    """ViewSet do zarządzania certyfikatami."""
    permission_classes = [permissions.IsAuthenticated]
    queryset = Certification.objects.select_related('technician__user', 'manufacturer').all()
    serializer_class = CertificationSerializer


# --- Widoki niestandardowe i pomocnicze ---

class TechnicianListView(generics.ListAPIView):
    """Widok tylko do listowania aktywnych serwisantów (read-only)."""
    queryset = Technician.objects.select_related('user').filter(is_active=True)
    serializer_class = TechnicianSerializer
    permission_classes = [permissions.IsAuthenticated]


class RegisterView(generics.CreateAPIView):
    """Widok do rejestracji nowych użytkowników."""
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


# ZASTĄPIENIE FetchCompanyDataView widokiem funkcyjnym - czystsze i rozwiązuje problemy z IDE.
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def fetch_company_data(request, nip):
    """
    Widok funkcyjny do pobierania danych o firmie z API Białej Listy.
    """
    today = date.today().strftime("%Y-%m-%d")
    url = f"https://wl-api.mf.gov.pl/api/search/nip/{nip}?date={today}"

    try:
        with requests.Session() as session:
            response = session.get(url, timeout=10)
            response.raise_for_status()

        data = response.json()

        if 'code' in data and 'subject' not in data.get('result', {}):
             return Response({"detail": data.get('message', "Nie znaleziono firmy lub wystąpił błąd.")},
                            status=status.HTTP_404_NOT_FOUND)

        subject_data = data['result']['subject']
        cleaned_data = {
            'name': subject_data.get('name', ''),
            'nip': subject_data.get('nip', ''),
            'regon': subject_data.get('regon', ''),
            'address': subject_data.get('workingAddress') or subject_data.get('residenceAddress') or ''
        }
        return Response(cleaned_data, status=status.HTTP_200_OK)

    except requests.exceptions.Timeout:
        return Response({"detail": "Serwer Ministerstwa Finansów nie odpowiada. Spróbuj ponownie."},
                        status=status.HTTP_504_GATEWAY_TIMEOUT)
    except requests.exceptions.RequestException as e:
        print(f"Błąd połączenia z API MF: {e}") # Logowanie błędu na serwerze
        return Response(
            {"detail": "Nie można połączyć się z usługą Białej Listy. Sprawdź połączenie internetowe."},
            status=status.HTTP_503_SERVICE_UNAVAILABLE)