from rest_framework import serializers
from django.db.models import Count
from .models.users import CustomUser, Technician, Company
from .models.clients import Client
from .models.manufacturers import Manufacturer, Certification
from .models.devices import FiscalDevice
from .models.tickets import ServiceTicket
from .models.billing import Order, ActivationCode

class CustomUserSerializer(serializers.ModelSerializer):
    """Serializer for reading user data."""

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
    """Simplified serializer for nested technician info."""
    full_name = serializers.CharField(source='full_name', read_only=True)

    class Meta:
        model = Technician
        fields = ['id', 'full_name']

class TechnicianReadSerializer(serializers.ModelSerializer):
    """Serializer for reading full technician info."""
    user = CustomUserSerializer(read_only=True)

    class Meta:
        model = Technician
        fields = ['id', 'user', 'phone_number', 'is_active']

class TechnicianWriteSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating technicians."""
    class Meta:
        model = Technician
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'is_active']

    def validate(self, data):
        """Ensure technician belongs to the request user's company."""
        request_user = self.context['request'].user
        if hasattr(request_user, 'company') and request_user.company is None:
            raise serializers.ValidationError("Your user must belong to a company to create technicians.")
        return data


class RegisterSerializer(serializers.ModelSerializer):
    """Handles user registration and creates associated technician profile."""
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    class Meta:
        model = CustomUser
        fields = ('username', 'password', 'email', 'first_name', 'last_name')

    def create(self, validated_data):
        user = CustomUser.objects.create_user(**validated_data)
        Technician.objects.create(user=user)
        return user


class ClientSummarySerializer(serializers.ModelSerializer):
    """Simplified client serializer for nesting."""
    class Meta:
        model = Client
        fields = ['id', 'name', 'nip']


class ClientReadSerializer(serializers.ModelSerializer):
    """Full client serializer."""
    class Meta:
        model = Client
        fields = ['id', 'name', 'address', 'nip', 'regon', 'phone_number', 'email', 'created_at']


class ClientWriteSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating clients, company-scoped."""
    class Meta:
        model = Client
        fields = ['name', 'address', 'nip', 'regon', 'phone_number', 'email']

    def validate(self, data):
        """Optionally enforce company scoping if needed."""
        return data

class ManufacturerSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Manufacturer
        fields = ['id', 'name']


class ManufacturerWriteSerializer(serializers.ModelSerializer):
    """Company-scoped manufacturer creation/update."""
    class Meta:
        model = Manufacturer
        fields = ['name']

    def validate(self, data):
        """Optionally ensure uniqueness within company if implemented."""
        return data


class CertificationReadSerializer(serializers.ModelSerializer):
    technician_name = serializers.CharField(source='technician.full_name', read_only=True)
    manufacturer_name = serializers.CharField(source='manufacturer.name', read_only=True)

    class Meta:
        model = Certification
        fields = [
            'id', 'technician_name', 'manufacturer_name',
            'certificate_number', 'issue_date', 'expiry_date'
        ]


class CertificationWriteSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating certifications, enforces company scoping."""

    class Meta:
        model = Certification
        fields = ['technician', 'manufacturer', 'certificate_number', 'issue_date', 'expiry_date']

    def validate(self, data):
        """Ensure technician and manufacturer belong to the request user's company."""
        company = self.context['request'].user.company
        technician = data.get('technician')
        manufacturer = data.get('manufacturer')

        if technician and hasattr(technician, 'user') and technician.user.company != company:
            raise serializers.ValidationError({"technician": "Technician does not belong to your company."})

        if manufacturer and getattr(manufacturer, 'company', company) != company:
            raise serializers.ValidationError({"manufacturer": "Manufacturer does not belong to your company."})

        return data


class FiscalDeviceReadSerializer(serializers.ModelSerializer):
    """Read-only fiscal device serializer with nested owner and brand."""
    owner = ClientSummarySerializer(read_only=True)
    brand = ManufacturerSummarySerializer(read_only=True)
    tickets_count = serializers.IntegerField(read_only=True)
    status = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = FiscalDevice
        fields = [
            'id', 'brand', 'model_name', 'unique_number', 'serial_number',
            'sale_date', 'last_service_date', 'status', 'operating_instructions',
            'remarks', 'owner', 'tickets_count'
        ]


class FiscalDeviceWriteSerializer(serializers.ModelSerializer):
    owner = serializers.PrimaryKeyRelatedField(queryset=Client.objects.all())
    brand = serializers.PrimaryKeyRelatedField(queryset=Manufacturer.objects.all())

    class Meta:
        model = FiscalDevice
        fields = [
            'brand', 'model_name', 'unique_number', 'serial_number', 'sale_date',
            'last_service_date', 'status', 'operating_instructions', 'remarks', 'owner'
        ]

    def validate(self, data):
        """Ensure that owner and brand belong to the user's company."""
        company = self.context['request'].user.company
        owner = data.get('owner')
        brand = data.get('brand')

        if owner and getattr(owner, 'company', company) != company:
            raise serializers.ValidationError({"owner": "Client does not belong to your company."})

        if brand and getattr(brand, 'company', company) != company:
            raise serializers.ValidationError({"brand": "Manufacturer does not belong to your company."})

        return data


class ServiceTicketReadSerializer(serializers.ModelSerializer):
    client = ClientSummarySerializer(read_only=True)
    device_info = serializers.CharField(source='device.model_name', read_only=True)
    assigned_technician = TechnicianSummarySerializer(read_only=True)
    status = serializers.CharField(source='get_status_display', read_only=True)
    ticket_type = serializers.CharField(source='get_ticket_type_display', read_only=True)

    class Meta:
        model = ServiceTicket
        fields = [
            'id', 'ticket_number', 'title', 'description', 'ticket_type', 'status',
            'client', 'device', 'device_info', 'assigned_technician',
            'created_at', 'scheduled_for', 'completed_at', 'resolution_notes'
        ]
        extra_kwargs = {
            'device': {'write_only': True}  # Only allow writing device via ID
        }


class ServiceTicketWriteSerializer(serializers.ModelSerializer):
    client = serializers.PrimaryKeyRelatedField(queryset=Client.objects.all())
    device = serializers.PrimaryKeyRelatedField(queryset=FiscalDevice.objects.all())
    assigned_technician = serializers.PrimaryKeyRelatedField(queryset=Technician.objects.all(),
                                                            allow_null=True, required=False)

    class Meta:
        model = ServiceTicket
        fields = [
            'title', 'description', 'ticket_type', 'status', 'client', 'device',
            'assigned_technician', 'scheduled_for', 'resolution_notes'
        ]

    def validate(self, data):
        """Ensure device belongs to selected client."""
        client = data.get('client')
        device = data.get('device')

        if client and device and device.owner != client:
            raise serializers.ValidationError({"device": "Selected device does not belong to this client."})

        return data

class OrderReadSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source='company.name', read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'company', 'company_name', 'email', 'stripe_session_id',
                  'stripe_payment_intent', 'status', 'amount_cents', 'currency',
                  'created_at', 'updated_at']


class OrderWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['company', 'email', 'stripe_session_id', 'stripe_payment_intent', 'status', 'amount_cents', 'currency']


class ActivationCodeReadSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source='company.name', read_only=True)
    used_by_username = serializers.CharField(source='used_by.username', read_only=True)

    class Meta:
        model = ActivationCode
        fields = ['code', 'order', 'company', 'company_name', 'email', 'used', 'used_by', 'used_by_username', 'created_at', 'expires_at']


class ActivationCodeWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivationCode
        fields = ['code', 'order', 'company', 'email', 'used', 'used_by']