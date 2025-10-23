from rest_framework import serializers
from .models import CustomUser, Client, FiscalDevice, ServiceRecord


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ['id', 'name', 'address', 'nip', 'phone_number', 'email', 'created_at', 'regon']


class ServiceRecordSerializer(serializers.ModelSerializer):
    technician_username = serializers.ReadOnlyField(source='technician.username')

    class Meta:
        model = ServiceRecord
        fields = ['id', 'description', 'service_date', 'device', 'technician', 'technician_username']
        read_only_fields = ['technician_username']


class FiscalDeviceSerializer(serializers.ModelSerializer):
    owner_name = serializers.ReadOnlyField(source='owner.name')
    service_history = ServiceRecordSerializer(many=True, read_only=True)

    class Meta:
        model = FiscalDevice
        fields = [
            'id',
            'brand_name',
            'model_name',
            'unique_number',
            'serial_number',
            'sale_date',
            'last_service_date',
            'status',
            'operating_instructions',
            'remarks',
            'owner',
            'owner_name',
            'service_history'
        ]
        read_only_fields = ['owner_name', 'service_history']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    class Meta:
        model = CustomUser
        fields = ('username', 'password', 'email', 'first_name', 'last_name')
        extra_kwargs = {'email': {'required': True}}

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            email=validated_data['email'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        return user