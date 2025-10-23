from rest_framework import serializers
from .models import (
    CustomUser, Client, Manufacturer, Technician, Certification, FiscalDevice, ServiceTicket
)

# --- Serializery Użytkowników i Serwisantów ---

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

class TechnicianSerializer(serializers.ModelSerializer):
    # Zagnieżdżamy dane użytkownika, aby mieć od razu jego imię i nazwisko
    user = CustomUserSerializer(read_only=True)

    class Meta:
        model = Technician
        fields = ['id', 'user', 'phone_number', 'is_active']

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = CustomUser
        fields = ('username', 'password', 'email', 'first_name', 'last_name')
        extra_kwargs = {'email': {'required': True}}

    def create(self, validated_data):
        user = CustomUser.objects.create_user(**validated_data)
        # Automatycznie tworzymy profil serwisanta dla nowego użytkownika
        Technician.objects.create(user=user)
        return user


# --- Serializery Słownikowe ---

class ManufacturerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Manufacturer
        fields = '__all__'

class CertificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certification
        fields = '__all__'


# --- Serializery Główne ---

class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ['id', 'name', 'address', 'nip', 'phone_number', 'email', 'created_at', 'regon']

# --- Zaktualizowany Serializer dla Zgłoszeń ---

class ServiceTicketSerializer(serializers.ModelSerializer):
    # Używamy zagnieżdżonych serializerów, aby zwracać czytelne dane, a nie tylko ID
    client_name = serializers.CharField(source='client.name', read_only=True)
    device_info = serializers.CharField(source='device.__str__', read_only=True)
    technician_name = serializers.CharField(source='assigned_technician.__str__', read_only=True, allow_null=True)

    class Meta:
        model = ServiceTicket
        fields = [
            'id', 'ticket_number', 'title', 'description', 'ticket_type', 'status',
            'client', 'client_name', 'device', 'device_info', 'assigned_technician', 'technician_name',
            'created_at', 'resolution_notes', 'scheduled_for', 'completed_at'
        ]
        # Klient, urządzenie i serwisant są podawani jako ID przy tworzeniu/edycji
        read_only_fields = ['ticket_number', 'created_at', 'completed_at', 'client_name', 'device_info', 'technician_name']


# --- Zaktualizowany Serializer dla Urządzeń ---

class FiscalDeviceSerializer(serializers.ModelSerializer):
    owner_name = serializers.CharField(source='owner.name', read_only=True)
    brand_name = serializers.CharField(source='brand.name', read_only=True)
    tickets = ServiceTicketSerializer(many=True, read_only=True, source='tickets')

    class Meta:
        model = FiscalDevice
        fields = [
            'id', 'brand', 'brand_name', 'model_name', 'unique_number', 'serial_number',
            'sale_date', 'last_service_date', 'status', 'operating_instructions',
            'remarks', 'owner', 'owner_name', 'tickets'
        ]
        read_only_fields = ['owner_name', 'brand_name', 'tickets']