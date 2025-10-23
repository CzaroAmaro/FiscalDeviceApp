import requests
from datetime import date
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics, permissions

from .models import Client, FiscalDevice, ServiceRecord
from .serializers import ClientSerializer, FiscalDeviceSerializer, ServiceRecordSerializer, RegisterSerializer

# --- Widoki do zarządzania Klientami ---

class ClientListCreateView(generics.ListCreateAPIView):
    """
    Widok do listowania i tworzenia klientów.
    GET /api/clients/ -> Zwraca listę wszystkich klientów.
    POST /api/clients/ -> Tworzy nowego klienta.
    """
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    permission_classes = [permissions.IsAuthenticated]

class ClientDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Widok do wyświetlania, aktualizacji i usuwania pojedynczego klienta.
    GET /api/clients/{id}/ -> Zwraca dane jednego klienta.
    PUT/PATCH /api/clients/{id}/ -> Aktualizuje dane klienta.
    DELETE /api/clients/{id}/ -> Usuwa klienta.
    """
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

# --- Widoki do zarządzania Historią Serwisową ---

class ServiceRecordListCreateView(generics.ListCreateAPIView):
    serializer_class = ServiceRecordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Filtrujemy wpisy serwisowe, aby pokazać tylko te,
        które należą do urządzenia o zadanym ID w URL.
        np. /api/devices/5/history/
        """
        device_id = self.kwargs['device_pk']
        return ServiceRecord.objects.filter(device_id=device_id)

    def perform_create(self, serializer):
        """
        Automatycznie przypisujemy tworzony wpis serwisowy
        do urządzenia z URL oraz do zalogowanego użytkownika.
        """
        device_id = self.kwargs['device_pk']
        device = FiscalDevice.objects.get(pk=device_id)
        serializer.save(technician=self.request.user, device=device)

# --- Widok do Rejestracji Użytkownika ---

class RegisterView(generics.CreateAPIView):
    """
    Widok do rejestracji nowych użytkowników. Dostępny dla wszystkich.
    POST /api/register/ -> Tworzy nowego użytkownika.
    """
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

class FetchCompanyDataView(APIView):
        """
        Pobiera dane firmy z API Białej Listy MF na podstawie numeru NIP.
        Wymaga autentykacji.
        Endpoint: GET /api/company-data/<nip>/
        """
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
