import requests
from datetime import date
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics, permissions

from .models import (
    Client, FiscalDevice, ServiceTicket, Manufacturer, Technician, Certification
)
from .serializers import (
    ClientSerializer, FiscalDeviceSerializer, ServiceTicketSerializer,
    RegisterSerializer, ManufacturerSerializer, TechnicianSerializer,
    CertificationSerializer
)

# --- Widoki do zarządzania Klientami ---
class ClientListCreateView(generics.ListCreateAPIView):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    permission_classes = [permissions.IsAuthenticated]

class ClientDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    permission_classes = [permissions.IsAuthenticated]

# --- Widoki do zarządzania Urządzeniami Fiskalnymi ---
class FiscalDeviceListCreateView(generics.ListCreateAPIView):
    queryset = FiscalDevice.objects.all()
    serializer_class = FiscalDeviceSerializer
    permission_classes = [permissions.IsAuthenticated]

class FiscalDeviceDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = FiscalDevice.objects.all()
    serializer_class = FiscalDeviceSerializer
    permission_classes = [permissions.IsAuthenticated]

# --- NOWE Widoki dla Nowych Modeli ---

class ManufacturerListCreateView(generics.ListCreateAPIView):
    queryset = Manufacturer.objects.all()
    serializer_class = ManufacturerSerializer
    permission_classes = [permissions.IsAuthenticated]

class TechnicianListView(generics.ListAPIView):
    queryset = Technician.objects.filter(is_active=True)
    serializer_class = TechnicianSerializer
    permission_classes = [permissions.IsAuthenticated]

class CertificationListCreateView(generics.ListCreateAPIView):
    queryset = Certification.objects.all()
    serializer_class = CertificationSerializer
    permission_classes = [permissions.IsAuthenticated]

# --- ZAKTUALIZOWANY Widok dla Zgłoszeń Serwisowych ---

class ServiceTicketListCreateView(generics.ListCreateAPIView):
    queryset = ServiceTicket.objects.all()
    serializer_class = ServiceTicketSerializer
    permission_classes = [permissions.IsAuthenticated]
    # Można dodać filtrowanie, np. po statusie
    # filterset_fields = ['status', 'ticket_type', 'assigned_technician']

class ServiceTicketDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ServiceTicket.objects.all()
    serializer_class = ServiceTicketSerializer
    permission_classes = [permissions.IsAuthenticated]


# --- Widoki Pomocnicze i Autentykacji ---

class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

class FetchCompanyDataView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request, nip, format=None):
            """
            Obsługuje żądanie GET.
            """
            today = date.today().strftime("%Y-%m-%d")
            # URL do oficjalnego API Ministerstwa Finansów
            url = f"https://wl-api.mf.gov.pl/api/search/nip/{nip}?date={today}"

            try:
                # Używamy sesji, co jest dobrą praktyką do zarządzania połączeniami
                with requests.Session() as session:
                    response = session.get(url, timeout=10)  # Timeout na 10 sekund
                    response.raise_for_status()  # Rzuci błędem dla statusów 4xx/5xx (np. 404, 500)

                data = response.json()

                # Sprawdzanie, czy samo API MF nie zwróciło błędu wewnątrz poprawnej odpowiedzi 200 OK
                if 'code' in data and data['code'] != '200 OK':
                    return Response({"detail": data.get('message', 'Błąd API Ministerstwa Finansów.')},
                                    status=status.HTTP_400_BAD_REQUEST)

                # Wyciągamy interesujące nas dane z zagnieżdżonej struktury
                subject_data = data.get('result', {}).get('subject')

                if not subject_data:
                    return Response(
                        {"detail": "Nie znaleziono firmy o podanym numerze NIP w rejestrze VAT."},
                        status=status.HTTP_404_NOT_FOUND
                    )

                # Przygotowujemy czystą, prostą odpowiedź dla naszego frontendu
                cleaned_data = {
                    'name': subject_data.get('name', ''),
                    'nip': subject_data.get('nip', ''),
                    'regon': subject_data.get('regon', ''),
                    'address': subject_data.get('workingAddress') or subject_data.get('residenceAddress') or ''
                }

                return Response(cleaned_data, status=status.HTTP_200_OK)

            except requests.exceptions.Timeout:
                # Obsługa błędu, gdy serwer MF nie odpowiada na czas
                return Response({"detail": "Serwer Ministerstwa Finansów nie odpowiada. Spróbuj ponownie."},
                                status=status.HTTP_504_GATEWAY_TIMEOUT)
            except requests.exceptions.RequestException as e:
                # Obsługa ogólnych błędów sieciowych (np. brak internetu)
                print(f"Błąd połączenia z API MF: {e}")  # Logowanie błędu na serwerze
                return Response(
                    {"detail": "Nie można połączyć się z usługą Białej Listy. Sprawdź połączenie internetowe."},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE)
