from rest_framework import serializers
from .models import (
    CustomUser, Client, Manufacturer, Technician, Certification, FiscalDevice, ServiceTicket
)


# --- Serializery Użytkowników i Serwisantów ---

class CustomUserSerializer(serializers.ModelSerializer):
    """Serializer do odczytu danych użytkownika."""

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


class TechnicianSerializer(serializers.ModelSerializer):
    """Serializer do odczytu pełnych danych o serwisancie."""
    user = CustomUserSerializer(read_only=True)

    class Meta:
        model = Technician
        fields = ['id', 'user', 'phone_number', 'is_active']


class TechnicianSummarySerializer(serializers.ModelSerializer):
    """Uproszczony serializer do zagnieżdżania w innych obiektach (np. w zgłoszeniu)."""
    full_name = serializers.CharField(source='__str__', read_only=True)

    class Meta:
        model = Technician
        fields = ['id', 'full_name']


class RegisterSerializer(serializers.ModelSerializer):
    """Serializer do rejestracji nowego użytkownika i tworzenia jego profilu serwisanta."""
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    class Meta:
        model = CustomUser
        fields = ('username', 'password', 'email', 'first_name', 'last_name')

    def create(self, validated_data):
        # Użycie create_user zapewnia poprawne hashowanie hasła
        user = CustomUser.objects.create_user(**validated_data)
        # Automatycznie tworzymy profil serwisanta dla nowego użytkownika
        Technician.objects.create(user=user)
        return user


# --- Serializery Słownikowe i Klientów ---

class ManufacturerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Manufacturer
        fields = ['id', 'name']  # Lepsza praktyka niż '__all__'


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ['id', 'name', 'address', 'nip', 'phone_number', 'email', 'regon', 'created_at']


class ClientSummarySerializer(serializers.ModelSerializer):
    """Uproszczony serializer do zagnieżdżania (np. w zgłoszeniu)."""

    class Meta:
        model = Client
        fields = ['id', 'name', 'nip']


# --- Serializery Urządzeń Fiskalnych (z podziałem na odczyt i zapis) ---

class FiscalDeviceSerializer(serializers.ModelSerializer):
    """
    Serializer do odczytu (lista/detale) urządzeń. Zwraca czytelne nazwy.
    """
    # Zamiast pól _name, zagnieżdżamy uproszczone serializery
    owner = ClientSummarySerializer(read_only=True)
    brand = ManufacturerSerializer(read_only=True)
    # Zamiast pełnych zgłoszeń, zwracamy tylko liczbę zgłoszeń (wydajność!)
    tickets_count = serializers.IntegerField(source='tickets.count', read_only=True)
    # Lepszy sposób na wyświetlanie wartości z `choices`
    status = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = FiscalDevice
        fields = [
            'id', 'brand', 'model_name', 'unique_number', 'serial_number',
            'sale_date', 'last_service_date', 'status', 'operating_instructions',
            'remarks', 'owner', 'tickets_count'
        ]


class FiscalDeviceWriteSerializer(serializers.ModelSerializer):
    """
    Serializer do tworzenia i aktualizacji urządzeń. Akceptuje ID dla relacji.
    """
    # pola relacji jawnie zdefiniowane, aby DRF wiedział, że oczekuje ID
    owner = serializers.PrimaryKeyRelatedField(queryset=Client.objects.all())
    brand = serializers.PrimaryKeyRelatedField(queryset=Manufacturer.objects.all())

    class Meta:
        model = FiscalDevice
        fields = [
            'brand', 'model_name', 'unique_number', 'serial_number', 'sale_date',
            'last_service_date', 'status', 'operating_instructions', 'remarks', 'owner'
        ]


# --- Serializery Zgłoszeń Serwisowych (z podziałem na odczyt i zapis) ---

class ServiceTicketSerializer(serializers.ModelSerializer):
    """
    Serializer do odczytu (lista/detale) zgłoszeń. Zwraca zagnieżdżone obiekty.
    """
    client = ClientSummarySerializer(read_only=True)
    # Użycie __str__ jest OK, ale dedykowany serializer jest bardziej elastyczny
    device_info = serializers.CharField(source='device.__str__', read_only=True)
    assigned_technician = TechnicianSummarySerializer(read_only=True)
    # Lepszy sposób na wyświetlanie wartości z `choices`
    status = serializers.CharField(source='get_status_display', read_only=True)
    ticket_type = serializers.CharField(source='get_ticket_type_display', read_only=True)

    class Meta:
        model = ServiceTicket
        fields = [
            'id', 'ticket_number', 'title', 'description', 'ticket_type', 'status',
            'client', 'device', 'device_info', 'assigned_technician',
            'created_at', 'scheduled_for', 'completed_at', 'resolution_notes'
        ]
        # Pole 'device' jest tu tylko dla ID
        extra_kwargs = {
            'device': {'write_only': True}
        }


class ServiceTicketWriteSerializer(serializers.ModelSerializer):
    """
    Serializer do tworzenia i aktualizacji zgłoszeń. Prosty i wydajny.
    """
    # Jawne zdefiniowanie pól relacji jako PrimaryKeyRelatedField
    client = serializers.PrimaryKeyRelatedField(queryset=Client.objects.all())
    device = serializers.PrimaryKeyRelatedField(queryset=FiscalDevice.objects.all())
    assigned_technician = serializers.PrimaryKeyRelatedField(
        queryset=Technician.objects.all(),
        allow_null=True,  # Zgodnie z modelem
        required=False
    )

    class Meta:
        model = ServiceTicket
        fields = [
            'title', 'description', 'ticket_type', 'status', 'client', 'device',
            'assigned_technician', 'scheduled_for', 'resolution_notes'
        ]

    def validate(self, data):
        """
        Dodatkowa walidacja - sprawdzenie, czy wybrane urządzenie należy do wybranego klienta.
        """
        client = data.get('client')
        device = data.get('device')

        if client and device and device.owner != client:
            raise serializers.ValidationError({
                "device": "Wybrane urządzenie nie należy do tego klienta."
            })
        return data

class CertificationSerializer(serializers.ModelSerializer):
    """
    Serializer dla certyfikatów.
    Zwraca czytelne nazwy, a przy zapisie akceptuje ID.
    """
    # Pola do odczytu, które zwracają czytelne nazwy zamiast ID
    technician_name = serializers.CharField(source='technician.__str__', read_only=True)
    manufacturer_name = serializers.CharField(source='manufacturer.name', read_only=True)

    class Meta:
        model = Certification
        fields = [
            'id', 'technician', 'technician_name', 'manufacturer', 'manufacturer_name',
            'certificate_number', 'issue_date', 'expiry_date'
        ]
        # Ustawiamy pola relacji jako write_only.
        # Przy żądaniu POST/PUT będziemy wysyłać ID technika i producenta.
        # W odpowiedzi (GET) te pola nie będą widoczne, zamiast nich pojawią się
        # pola _name zdefiniowane powyżej.
        extra_kwargs = {
            'technician': {'write_only': True},
            'manufacturer': {'write_only': True},
        }