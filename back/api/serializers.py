from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from rest_framework import serializers
from .models.users import CustomUser, Technician, Company
from .models.clients import Client
from .models.manufacturers import Manufacturer, Certification
from .models.devices import FiscalDevice, DeviceHistoryEntry
from .models.tickets import ServiceTicket
from .models.billing import Order, ActivationCode
from dateutil.relativedelta import relativedelta
from geopy.geocoders import Nominatim

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['id', 'name', 'created_at']
        read_only_fields = ['id', 'created_at']

class CustomUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


class TechnicianSummarySerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = Technician
        fields = ['id', 'full_name']


class TechnicianReadSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer(read_only=True)
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = Technician
        fields = ['id', 'user', 'first_name', 'last_name', 'email', 'phone_number', 'is_active', 'role', 'role_display','full_name']


class TechnicianWriteSerializer(serializers.ModelSerializer):
    create_user_account = serializers.BooleanField(write_only=True, default=False)
    username = serializers.CharField(write_only=True, required=False, allow_blank=True)
    password = serializers.CharField(write_only=True, required=False, allow_blank=True,style={'input_type': 'password'})

    class Meta:
        model = Technician
        fields = (
            'id', 'first_name', 'last_name', 'email', 'phone_number', 'is_active', 'role', 'create_user_account', 'username', 'password')
        read_only_fields = ('id',)

    def validate(self, data):
        if self.context['request'].method == 'POST' and data.get('create_user_account'):
            if not data.get('username'):
                raise serializers.ValidationError({"username": "Nazwa użytkownika jest wymagana."})
            if not data.get('password'):
                raise serializers.ValidationError({"password": "Hasło jest wymagane."})
            if CustomUser.objects.filter(username=data['username']).exists():
                raise serializers.ValidationError({"username": "Użytkownik o tej nazwie już istnieje."})
            if CustomUser.objects.filter(email=data['email']).exists():
                raise serializers.ValidationError({"email": "Użytkownik z tym adresem e-mail już istnieje."})
            try:
                validate_password(data['password'])
            except Exception as e:
                raise serializers.ValidationError({"password": list(e.messages)})
        return data

    @transaction.atomic
    def create(self, validated_data):
        admin_user = self.context['request'].user
        company = admin_user.technician_profile.company

        create_account = validated_data.pop('create_user_account', False)
        username = validated_data.pop('username', None)
        password = validated_data.pop('password', None)

        user_obj = None
        if create_account:
            user_obj = CustomUser.objects.create_user(
                username=username,
                email=validated_data.get('email'),
                password=password,
                first_name=validated_data.get('first_name', ''),
                last_name=validated_data.get('last_name', ''),
            )

        technician = Technician.objects.create(user=user_obj, company=company, **validated_data)
        return technician

    @transaction.atomic
    def update(self, instance, validated_data):
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.email = validated_data.get('email', instance.email)
        instance.phone_number = validated_data.get('phone_number', instance.phone_number)
        instance.is_active = validated_data.get('is_active', instance.is_active)
        instance.role = validated_data.get('role', instance.role)
        instance.save()

        if instance.user:
            instance.user.first_name = instance.first_name
            instance.user.last_name = instance.last_name
            instance.user.email = instance.email
            instance.user.save()

        return instance


class NestedTechnicianProfileSerializer(serializers.ModelSerializer):
    is_admin = serializers.SerializerMethodField()
    class Meta:
        model = Technician
        fields = ['id', 'company', 'is_admin']
    def get_is_admin(self, obj):
        return obj.is_admin

class UserProfileSerializer(serializers.ModelSerializer):
    technician_profile = NestedTechnicianProfileSerializer(read_only=True)

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'technician_profile']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    class Meta:
        model = CustomUser
        fields = ('username', 'password', 'email', 'first_name', 'last_name')

    def validate_email(self, value):
        if CustomUser.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Użytkownik z tym adresem e-mail już istnieje.")
        return value

    def create(self, validated_data):
        user = CustomUser.objects.create_user(**validated_data)
        # Technician creation moved to registration view (requires activation code/company)
        return user

class ClientSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ['id', 'name', 'nip']


class ClientLocationSerializer(serializers.ModelSerializer):
    has_open_tickets = serializers.BooleanField(read_only=True)

    class Meta:
        model = Client
        fields = ['id', 'name', 'latitude', 'longitude', 'has_open_tickets']


class ClientReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ['id', 'company', 'name', 'address', 'nip', 'regon', 'phone_number', 'email', 'created_at', 'latitude', 'longitude']
        read_only_fields = fields


class ClientWriteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Client
        fields = ['name', 'address', 'nip', 'regon', 'phone_number', 'email']

    def geocode(self, address):
        geolocator = Nominatim(user_agent="myapp")
        location = geolocator.geocode(address)
        if location:
            return location.latitude, location.longitude
        return None, None

    def create(self, validated_data):
        address = validated_data.get('address')
        if address:
            lat, lng = self.geocode(address)
            validated_data['latitude'] = lat
            validated_data['longitude'] = lng

        request = self.context['request']
        company = request.user.technician_profile.company
        validated_data['company'] = company

        return Client.objects.create(**validated_data)

    def update(self, instance, validated_data):
        new_address = validated_data.get('address', instance.address)
        if new_address != instance.address:
            lat, lng = self.geocode(new_address)
            validated_data['latitude'] = lat
            validated_data['longitude'] = lng

        return super().update(instance, validated_data)

    def validate_nip(self, value):
        return value

class ManufacturerSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Manufacturer
        fields = ['id', 'name']


class ManufacturerWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Manufacturer
        fields = ['name']

    def validate(self, data):
        request = self.context['request']
        company = request.user.technician_profile.company
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

    class Meta:
        model = Certification
        fields = ['technician', 'manufacturer', 'certificate_number', 'issue_date', 'expiry_date']

    def validate(self, data):
        request = self.context['request']
        if not hasattr(request.user, 'technician_profile'):
            raise serializers.ValidationError("Użytkownik nie jest przypisany do żadnej firmy.")
        company = request.user.technician_profile.company
        tech = data.get('technician')
        manufacturer = data.get('manufacturer')

        if tech and tech.company != company:
            raise serializers.ValidationError({"technician": "Technician does not belong to your company."})
        if manufacturer and manufacturer.company != company:
            raise serializers.ValidationError({"manufacturer": "Manufacturer does not belong to your company."})
        return data

class DeviceHistoryEntrySerializer(serializers.ModelSerializer):
    action_type_display = serializers.CharField(source='get_action_type_display', read_only=True)
    actor_name = serializers.CharField(source='actor.username', read_only=True, allow_null=True)

    class Meta:
        model = DeviceHistoryEntry
        fields = ['id', 'event_date', 'action_type', 'action_type_display', 'description', 'actor_name']
        read_only_fields = fields

class FiscalDeviceReadSerializer(serializers.ModelSerializer):
    owner = ClientSummarySerializer(read_only=True)
    brand = ManufacturerSummarySerializer(read_only=True)
    tickets_count = serializers.IntegerField(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    next_service_date = serializers.SerializerMethodField()
    history_entries = DeviceHistoryEntrySerializer(many=True, read_only=True)

    class Meta:
        model = FiscalDevice
        fields = ['id', 'brand', 'model_name', 'unique_number', 'serial_number', 'sale_date', 'last_service_date', 'next_service_date', 'status', 'status_display', 'operating_instructions', 'remarks', 'owner', 'tickets_count', 'history_entries']

    def get_next_service_date(self, obj: FiscalDevice):
        if obj.last_service_date:
            return obj.last_service_date + relativedelta(years=2)
        return None


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

class ServiceTicketTechnicianUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceTicket
        fields = ['status', 'resolution_notes']


class ServiceTicketResolveSerializer(serializers.ModelSerializer):
    resolution = serializers.ChoiceField(choices=ServiceTicket.Resolution.choices)

    class Meta:
        model = ServiceTicket
        fields = ['resolution', 'resolution_notes']
        extra_kwargs = {
            'resolution_notes': {'required': False, 'allow_blank': True}
        }

    def validate_resolution(self, value):
        if value == ServiceTicket.Resolution.UNRESOLVED:
            raise serializers.ValidationError("Cannot set resolution back to 'unresolved' via this action.")
        return value

class ServiceTicketReadSerializer(serializers.ModelSerializer):
    client = ClientSummarySerializer(read_only=True)
    device_info = serializers.CharField(source='device.model_name', read_only=True)
    assigned_technician = TechnicianSummarySerializer(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    ticket_type_display = serializers.CharField(source='get_ticket_type_display', read_only=True)
    resolution_display = serializers.CharField(source='get_resolution_display', read_only=True)

    class Meta:
        model = ServiceTicket
        fields = [
            'id', 'ticket_number', 'title', 'description', 'ticket_type', 'ticket_type_display',
            'status', 'status_display', 'client', 'device', 'device_info', 'assigned_technician',
            'created_at', 'scheduled_for', 'completed_at', 'resolution', 'resolution_display', 'resolution_notes' # ZMIANA
        ]

class ServiceTicketWriteSerializer(serializers.ModelSerializer):
    client = serializers.PrimaryKeyRelatedField(queryset=Client.objects.none())
    device = serializers.PrimaryKeyRelatedField(queryset=FiscalDevice.objects.none())
    assigned_technician = serializers.PrimaryKeyRelatedField(
        queryset=Technician.objects.none(), allow_null=True, required=False
    )

    class Meta:
        model = ServiceTicket
        fields = [
            'title', 'description', 'ticket_type', 'client',
            'device', 'assigned_technician', 'scheduled_for'
        ]
        read_only_fields = ('status',)

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
        if not hasattr(request.user, 'technician_profile'):
            raise serializers.ValidationError("Użytkownik nie jest przypisany do żadnej firmy.")
        company = request.user.technician_profile.company

        if order and order.company != company:
            raise serializers.ValidationError({"order": "Order does not belong to your company."})
        return data


class ReportParameterSerializer(serializers.Serializer):
    date_from = serializers.DateField(required=False, help_text="Data sprzedaży od")
    date_to = serializers.DateField(required=False, help_text="Data sprzedaży do")

    clients = serializers.ListField(
        child=serializers.IntegerField(), required=False
    )
    devices = serializers.ListField(
        child=serializers.IntegerField(), required=False
    )
    device_brands = serializers.ListField(
        child=serializers.IntegerField(), required=False
    )

    include_service_history = serializers.BooleanField(default=False, help_text="Dołącz historię zleceń serwisowych")

    history_date_from = serializers.DateField(required=False)
    history_date_to = serializers.DateField(required=False)

    include_event_log = serializers.BooleanField(default=False, help_text="Dołącz dziennik zdarzeń (przeglądy, etc.)")

    output_format = serializers.ChoiceField(
        choices=['json', 'csv', 'pdf'], default='json', required=False
    )

    def validate(self, data):
        if 'date_from' in data and 'date_to' in data and data['date_from'] > data['date_to']:
            raise serializers.ValidationError("Data 'od' nie może być późniejsza niż data 'do'.")
        return data


class ReportResultSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source='client.name')
    client_nip = serializers.CharField(source='client.nip')
    device_model = serializers.CharField(source='device.model_name')
    device_unique_number = serializers.CharField(source='device.unique_number')
    assigned_technician_name = serializers.CharField(source='assigned_technician.full_name', allow_null=True)
    status_display = serializers.CharField(source='get_status_display')
    ticket_type_display = serializers.CharField(source='get_ticket_type_display')
    resolution_display = serializers.CharField(source='get_resolution_display')

    class Meta:
        model = ServiceTicket
        fields = (
            'ticket_number', 'title', 'created_at', 'scheduled_for', 'completed_at',
            'client_name', 'client_nip', 'device_model', 'device_unique_number',
            'assigned_technician_name', 'status_display', 'ticket_type_display', 'resolution_display'
        )

class ChangeEmailSerializer(serializers.Serializer):
    new_email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True, style={'input_type': 'password'})

    def validate_new_email(self, value):
        if CustomUser.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Ten adres e-mail jest już zajęty.")
        return value

class ConfirmEmailChangeSerializer(serializers.Serializer):
    token = serializers.CharField(required=True)

class AiSuggestionRequestSerializer(serializers.Serializer):
    description = serializers.CharField(required=True, min_length=10, max_length=2048, trim_whitespace=True)

class UserProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name']

    def update(self, instance, validated_data):
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.save()

        if hasattr(instance, 'technician_profile'):
            profile = instance.technician_profile
            profile.first_name = instance.first_name
            profile.last_name = instance.last_name
            profile.save(update_fields=['first_name', 'last_name'])

        return instance