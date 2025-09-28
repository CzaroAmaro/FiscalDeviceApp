from rest_framework import generics, permissions
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