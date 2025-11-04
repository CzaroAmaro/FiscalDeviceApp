from rest_framework import serializers
from .models.users import CustomUser, Technician
from .models.clients import Client
from .models.manufacturers import Manufacturer, Certification
from .models.devices import FiscalDevice
from .models.tickets import ServiceTicket
from .models.billing import Order, ActivationCode


# -----------------------------
# Users / Technicians
# -----------------------------

class CustomUserSerializer(serializers.ModelSerializer):
    """Serializer for reading user data."""

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


class TechnicianSummarySerializer(serializers.ModelSerializer):
    """Simplified serializer for nested technician info."""
    full_name = serializers.CharField(source='full_name', read_only=True)

    class Meta:
        model = Technician
        fields = ['id', 'full_name']


class TechnicianReadSerializer(serializers.ModelSerializer):
    """Serializer for reading full technician info."""
    user = CustomUserSerializer(read_only=True)
    company_name = serializers.CharField(source='company.name', read_only=True)

    class Meta:
        model = Technician
        fields = ['id', 'user', 'company', 'company_name', 'first_name', 'last_name', 'phone_number', 'is_active', 'is_company_admin']


class TechnicianWriteSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating technicians."""
    class Meta:
        model = Technician
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'is_active', 'is_company_admin']

    def validate(self, data):
        user = self.context['request'].user

        if not hasattr(user, 'technician_profile'):
            raise serializers.ValidationError(
                "Twoje konto musi być powiązane z profilem technika w firmie, aby wykonać tę akcję."
            )
        return data


class RegisterSerializer(serializers.ModelSerializer):
    """Handles user registration and creates associated technician profile."""
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    class Meta:
        model = CustomUser
        fields = ('username', 'password', 'email', 'first_name', 'last_name')

    def create(self, validated_data):
        user = CustomUser.objects.create_user(**validated_data)
        # Technician creation moved to registration view (requires activation code/company)
        return user


# -----------------------------
# Clients
# -----------------------------

class ClientSummarySerializer(serializers.ModelSerializer):
    """Simplified client serializer for nesting."""
    class Meta:
        model = Client
        fields = ['id', 'name', 'nip']


class ClientReadSerializer(serializers.ModelSerializer):
    """Full client serializer."""
    class Meta:
        model = Client
        fields = ['id', 'company', 'name', 'address', 'nip', 'regon', 'phone_number', 'email', 'created_at']


class ClientWriteSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating clients, company-scoped."""
    class Meta:
        model = Client
        fields = ['name', 'address', 'nip', 'regon', 'phone_number', 'email']

    def validate_nip(self, value):
        # NIP validated at model level; additionally ensure unique per company
        return value


# -----------------------------
# Manufacturers / Certifications
# -----------------------------

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
        request = self.context['request']
        company = request.user.company
        name = data.get('name')
        if Manufacturer.objects.filter(company=company, name__iexact=name).exists():
            raise serializers.ValidationError({"name": "Manufacturer with this name already exists in your company."})
        return data


class CertificationReadSerializer(serializers.ModelSerializer):
    technician_name = serializers.CharField(source='technician.full_name', read_only=True)
    manufacturer_name = serializers.CharField(source='manufacturer.name', read_only=True)

    class Meta:
        model = Certification
        fields = ['id', 'technician', 'technician_name', 'manufacturer', 'manufacturer_name', 'certificate_number', 'issue_date', 'expiry_date']


class CertificationWriteSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating certifications, enforces company scoping."""

    class Meta:
        model = Certification
        fields = ['technician', 'manufacturer', 'certificate_number', 'issue_date', 'expiry_date']

    def validate(self, data):
        request = self.context['request']
        company = request.user.company
        tech = data.get('technician')
        manufacturer = data.get('manufacturer')

        if tech and tech.company != company:
            raise serializers.ValidationError({"technician": "Technician does not belong to your company."})
        if manufacturer and manufacturer.company != company:
            raise serializers.ValidationError({"manufacturer": "Manufacturer does not belong to your company."})
        return data


# -----------------------------
# Fiscal Devices
# -----------------------------

class FiscalDeviceReadSerializer(serializers.ModelSerializer):
    """Read-only fiscal device serializer with nested owner and brand."""
    owner = ClientSummarySerializer(read_only=True)
    brand = ManufacturerSummarySerializer(read_only=True)
    tickets_count = serializers.IntegerField(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = FiscalDevice
        fields = ['id', 'brand', 'model_name', 'unique_number', 'serial_number', 'sale_date', 'last_service_date', 'status', 'status_display', 'operating_instructions', 'remarks', 'owner', 'tickets_count']


class FiscalDeviceWriteSerializer(serializers.ModelSerializer):
    owner = serializers.PrimaryKeyRelatedField(queryset=Client.objects.none())
    brand = serializers.PrimaryKeyRelatedField(queryset=Manufacturer.objects.none())

    class Meta:
        model = FiscalDevice
        fields = [
            'brand', 'model_name', 'unique_number', 'serial_number', 'sale_date',
            'last_service_date', 'status', 'operating_instructions', 'remarks', 'owner'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get('request')

        if request and hasattr(request.user, 'technician_profile'):
            company = request.user.technician_profile.company

            self.fields['owner'].queryset = Client.objects.filter(company=company)
            self.fields['brand'].queryset = Manufacturer.objects.filter(company=company)

    def validate(self, data):
        request = self.context['request']
        company = request.user.technician_profile.company

        owner = data.get('owner')
        brand = data.get('brand')

        if owner and owner.company != company:
            raise serializers.ValidationError({"owner": "Klient nie należy do Twojej firmy."})
        if brand and brand.company != company:
            raise serializers.ValidationError({"brand": "Producent nie należy do Twojej firmy."})

        return data

# -----------------------------
# Service Tickets
# -----------------------------

class ServiceTicketReadSerializer(serializers.ModelSerializer):
    client = ClientSummarySerializer(read_only=True)
    device_info = serializers.CharField(source='device.model_name', read_only=True)
    assigned_technician = TechnicianSummarySerializer(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    ticket_type_display = serializers.CharField(source='get_ticket_type_display', read_only=True)

    class Meta:
        model = ServiceTicket
        fields = ['id', 'ticket_number', 'title', 'description', 'ticket_type', 'ticket_type_display', 'status', 'status_display', 'client', 'device', 'device_info', 'assigned_technician', 'created_at', 'scheduled_for', 'completed_at', 'resolution_notes']
        extra_kwargs = {'device': {'write_only': True}}


class ServiceTicketWriteSerializer(serializers.ModelSerializer):
    client = serializers.PrimaryKeyRelatedField(queryset=Client.objects.none())
    device = serializers.PrimaryKeyRelatedField(queryset=FiscalDevice.objects.none())
    assigned_technician = serializers.PrimaryKeyRelatedField(
        queryset=Technician.objects.none(), allow_null=True, required=False
    )

    class Meta:
        model = ServiceTicket
        fields = [
            'title', 'description', 'ticket_type', 'status', 'client',
            'device', 'assigned_technician', 'scheduled_for', 'resolution_notes'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get('request')

        if request and hasattr(request.user, 'technician_profile'):
            company = request.user.technician_profile.company

            self.fields['client'].queryset = Client.objects.filter(company=company)
            self.fields['assigned_technician'].queryset = Technician.objects.filter(company=company)

            self.fields['device'].queryset = FiscalDevice.objects.filter(owner__company=company)

    def validate(self, data):
        request = self.context['request']
        company = request.user.technician_profile.company

        client = data.get('client')
        device = data.get('device')
        tech = data.get('assigned_technician')

        if client and client.company != company:
            raise serializers.ValidationError({"client": "Klient nie należy do Twojej firmy."})
        if device and device.owner != client:
            raise serializers.ValidationError({"device": "Wybrane urządzenie nie należy do tego klienta."})
        if tech and tech.company != company:
            raise serializers.ValidationError({"assigned_technician": "Serwisant nie należy do Twojej firmy."})

        return data


# -----------------------------
# Billing
# -----------------------------

class OrderReadSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source='company.name', read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'company', 'company_name', 'email', 'stripe_session_id', 'stripe_payment_intent', 'status', 'amount_cents', 'currency', 'created_at', 'updated_at']


class OrderWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['email', 'stripe_session_id', 'stripe_payment_intent', 'status', 'amount_cents', 'currency']


class ActivationCodeReadSerializer(serializers.ModelSerializer):
    order_id = serializers.UUIDField(source='order.id', read_only=True)
    company_name = serializers.CharField(source='order.company.name', read_only=True)
    used_by_username = serializers.CharField(source='used_by.username', read_only=True)

    class Meta:
        model = ActivationCode
        fields = ['code', 'order_id', 'company_name', 'email', 'used', 'used_by', 'used_by_username', 'created_at', 'expires_at']


class ActivationCodeWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivationCode
        fields = ['order', 'email', 'expires_at']

    def validate(self, data):
        request = self.context['request']
        order = data.get('order')
        if order and order.company != request.user.company:
            raise serializers.ValidationError({"order": "Order does not belong to your company."})
        return data
