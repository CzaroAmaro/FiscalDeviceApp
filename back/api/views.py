from datetime import timedelta, datetime
import requests

from django.db.models import Count
from django.utils import timezone
from rest_framework import viewsets, generics, permissions, status, filters
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend

from .models.users import Technician
from .models.clients import Client
from .models.manufacturers import Manufacturer, Certification
from .models.devices import FiscalDevice
from .models.tickets import ServiceTicket
from .models.billing import Order, ActivationCode

from .serializers import (
    CustomUserSerializer,
    RegisterSerializer,
    TechnicianReadSerializer, TechnicianWriteSerializer,
    ClientReadSerializer, ClientWriteSerializer,
    ManufacturerSummarySerializer, ManufacturerWriteSerializer,
    CertificationReadSerializer, CertificationWriteSerializer,
    FiscalDeviceReadSerializer, FiscalDeviceWriteSerializer,
    ServiceTicketReadSerializer, ServiceTicketWriteSerializer,
    OrderReadSerializer, OrderWriteSerializer,
    ActivationCodeReadSerializer, ActivationCodeWriteSerializer
)


# -------------------------
# Custom permissions
# -------------------------

class IsCompanyMember(permissions.BasePermission):
    """
    Allows access only to users who belong to a company.
    This permission alone doesn't check object ownership — querysets must be filtered.
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and hasattr(request.user, 'technician_profile'))


class IsCompanyAdmin(permissions.BasePermission):
    """
    Allows access only to company admins or staff/superuser.
    Assumes Technician.is_company_admin or user.is_staff/superuser.
    """
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if user.is_staff or user.is_superuser:
            return True
        if hasattr(user, 'technician_profile'):
            return user.technician_profile.is_company_admin
        return False


# -------------------------
# Registration
# -------------------------

class RegisterView(generics.CreateAPIView):
    """
    Registration endpoint that requires an activation code.
    If activation code is valid -> create user, create Technician linked to order.company, redeem code.
    """
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        activation_code_value = request.data.get('activation_code')
        if not activation_code_value:
            return Response({"activation_code": "This field is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Używamy select_related dla optymalizacji
            activation = ActivationCode.objects.select_related('order__company').get(code=activation_code_value)
        except ActivationCode.DoesNotExist:
            return Response({"activation_code": "Invalid activation code."}, status=status.HTTP_400_BAD_REQUEST)

        # Sprawdzenie, czy kod jest ważny (z użyciem metod z modelu)
        try:
            activation.redeem(user=None)  # Wstępna walidacja bez zapisu
        except ValueError as e:
            return Response({"activation_code": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # Stworzenie użytkownika
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Stworzenie profilu technika
        company = activation.order.company
        Technician.objects.create(
            user=user,
            company=company,
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
            is_active=True
        )

        # Ostateczne użycie kodu z przypisaniem do użytkownika
        activation.redeem(user)

        return Response(CustomUserSerializer(user).data, status=status.HTTP_201_CREATED)


# -------------------------
# Generic Company-Scoped ViewSet (Dla zmniejszenia powtórzeń)
# -------------------------

class CompanyScopedViewSet(viewsets.ModelViewSet):
    """
    Base ViewSet that automatically filters querysets by the user's company
    and assigns company on creation.
    """
    permission_classes = [permissions.IsAuthenticated, IsCompanyMember]

    def get_company(self):
        return self.request.user.technician_profile.company

    def get_queryset(self):
        return self.model.objects.filter(company=self.get_company())

    def perform_create(self, serializer):
        serializer.save(company=self.get_company())


# -------------------------
# Technicians
# -------------------------

class TechnicianViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, IsCompanyMember]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active', 'is_company_admin']
    search_fields = ['first_name', 'last_name', 'email', 'user__username']
    ordering_fields = ['first_name', 'last_name', 'is_company_admin']
    ordering = ['first_name', 'last_name']

    def get_queryset(self):
        company = self.request.user.technician_profile.company
        if self.request.user.is_staff or self.request.user.is_superuser or self.request.user.technician_profile.is_company_admin:
            return Technician.objects.select_related('user').filter(company=company)
        return Technician.objects.select_related('user').filter(user=self.request.user, company=company)

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return TechnicianWriteSerializer
        return TechnicianReadSerializer

    def perform_create(self, serializer):
        serializer.save(company=self.request.user.technician_profile.company)


# -------------------------
# Clients, Manufacturers (używają teraz CompanyScopedViewSet)
# -------------------------

class ClientViewSet(CompanyScopedViewSet):
    model = Client
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['nip']
    search_fields = ['name', 'nip', 'email']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return ClientWriteSerializer
        return ClientReadSerializer


class ManufacturerViewSet(CompanyScopedViewSet):
    model = Manufacturer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name']
    ordering = ['name']

    def get_serializer_class(self):
        if self.action == 'list':
            return ManufacturerSummarySerializer
        if self.action in ['create', 'update', 'partial_update']:
            return ManufacturerWriteSerializer
        return ManufacturerSummarySerializer  # lub pełny ReadSerializer jeśli istnieje


# -------------------------
# Certifications, Devices, Tickets (wymagają bardziej złożonego filtrowania)
# -------------------------

class CertificationViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, IsCompanyMember]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['manufacturer', 'technician']
    search_fields = ['certificate_number', 'manufacturer__name', 'technician__first_name', 'technician__last_name']
    ordering = ['-expiry_date']

    def get_queryset(self):
        company = self.request.user.technician_profile.company
        return Certification.objects.select_related('technician', 'manufacturer').filter(
            technician__company=company
        )

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return CertificationWriteSerializer
        return CertificationReadSerializer

    @action(detail=False, methods=['get'])
    def expiring(self, request):
        days = int(request.query_params.get('days', 30))
        threshold = timezone.now().date() + timedelta(days=days)
        qs = self.get_queryset().filter(expiry_date__lte=threshold).order_by('expiry_date')
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)


class FiscalDeviceViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, IsCompanyMember]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'brand']
    search_fields = ['model_name', 'serial_number', 'unique_number', 'owner__name']
    ordering = ['-sale_date']

    def get_queryset(self):
        company = self.request.user.technician_profile.company
        return FiscalDevice.objects.select_related('owner', 'brand').filter(
            owner__company=company
        ).annotate(tickets_count=Count('tickets'))

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return FiscalDeviceWriteSerializer
        return FiscalDeviceReadSerializer


class ServiceTicketViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, IsCompanyMember]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'ticket_type', 'assigned_technician', 'client', 'device']
    search_fields = ['ticket_number', 'title', 'description', 'client__name']
    ordering = ['-created_at']

    def get_queryset(self):
        company = self.request.user.technician_profile.company
        return ServiceTicket.objects.select_related('client', 'device__brand', 'assigned_technician__user').filter(
            client__company=company
        )

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return ServiceTicketWriteSerializer
        return ServiceTicketReadSerializer

    @action(detail=True, methods=['post'], permission_classes=[IsCompanyAdmin])
    def assign_technician(self, request):
        ticket = self.get_object()
        tech_id = request.data.get('technician_id')
        try:
            company = self.request.user.technician_profile.company
            tech = Technician.objects.get(id=tech_id, company=company)
        except Technician.DoesNotExist:
            return Response({'detail': 'Technician not found in your company.'}, status=status.HTTP_400_BAD_REQUEST)

        ticket.assigned_technician = tech
        ticket.save()
        return Response(ServiceTicketReadSerializer(ticket).data)

    @action(detail=True, methods=['post'])
    def change_status(self, request):
        ticket = self.get_object()
        new_status = request.data.get('status')
        if new_status not in ServiceTicket.Status:
            return Response({'detail': 'Invalid status.'}, status=status.HTTP_400_BAD_REQUEST)

        ticket.status = new_status
        if new_status == ServiceTicket.Status.CLOSED and not ticket.completed_at:
            ticket.completed_at = timezone.now()

        ticket.save()
        return Response(ServiceTicketReadSerializer(ticket).data)



class OrderViewSet(CompanyScopedViewSet):
    model = Order
    permission_classes = [IsCompanyAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'email']
    search_fields = ['stripe_payment_intent', 'stripe_session_id', 'email']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return OrderWriteSerializer
        return OrderReadSerializer

    @action(detail=True, methods=['post'])
    def create_activation_code(self, request):
        order = self.get_object()
        if order.status != 'paid':
            return Response({'detail': 'Order must be paid to create activation code.'},
                            status=status.HTTP_400_BAD_REQUEST)

        activation = ActivationCode.create_for_order(order, email=order.email)
        return Response(ActivationCodeReadSerializer(activation).data, status=status.HTTP_201_CREATED)


class ActivationCodeViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsCompanyAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['used', 'email']
    search_fields = ['code', 'email']
    ordering = ['-created_at']
    serializer_class = ActivationCodeReadSerializer

    def get_queryset(self):
        company = self.request.user.technician_profile.company
        return ActivationCode.objects.select_related('order', 'used_by').filter(order__company=company)


class DashboardView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsCompanyMember]

    def get(self, request):
        company = request.user.technician_profile.company

        thirty_days_from_now = timezone.now().date() + timedelta(days=30)

        stats = {
            "open_tickets": ServiceTicket.objects.filter(client__company=company,
                                                         status=ServiceTicket.Status.OPEN).count(),
            "devices_count": FiscalDevice.objects.filter(owner__company=company).count(),
            "clients_count": Client.objects.filter(company=company).count(),
            "expiring_certifications_30d": Certification.objects.filter(technician__company=company,
                                                                        expiry_date__lte=thirty_days_from_now).count()
        }
        return Response(stats, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def fetch_company_data(request, nip):
    today = datetime.today().strftime("%Y-%m-%d")
    url = f"https://wl-api.mf.gov.pl/api/search/nip/{nip}?date={today}"
    try:
        with requests.Session() as session:
            response = session.get(url, timeout=10)
            response.raise_for_status()
        data = response.json()
        if 'code' in data or 'subject' not in data.get('result', {}):
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
        return Response({"detail": "Serwer MF nie odpowiada."}, status=status.HTTP_504_GATEWAY_TIMEOUT)
    except requests.exceptions.RequestException as e:
        print(f"Fetch company data error: {e}")
        return Response({"detail": "Nie można połączyć się z usługą Białej Listy."},
                        status=status.HTTP_503_SERVICE_UNAVAILABLE)
