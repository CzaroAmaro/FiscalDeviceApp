import csv
from collections import defaultdict
from datetime import timedelta, datetime, date
import stripe
import requests
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt

from django.db.models import Count, Exists, OuterRef
from django.utils import timezone
from rest_framework import viewsets, generics, permissions, status, filters
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.renderers import JSONRenderer, BaseRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated

from .models.users import Technician, Company, CustomUser
from .models.clients import Client
from .models.manufacturers import Manufacturer, Certification
from .models.devices import FiscalDevice, DeviceHistoryEntry
from .models.tickets import ServiceTicket
from .models.billing import Order, ActivationCode

from django.db.models import Q

from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML
import json
import google.generativeai as genai

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
    ActivationCodeReadSerializer, ActivationCodeWriteSerializer, CompanySerializer, UserProfileSerializer,
    ServiceTicketTechnicianUpdateSerializer, ServiceTicketResolveSerializer, ClientLocationSerializer,
    ReportResultSerializer, ReportParameterSerializer, ConfirmEmailChangeSerializer, ChangeEmailSerializer,
    AiSuggestionRequestSerializer, TechnicianSummarySerializer
)

class IsCompanyMember(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False

        if user.is_superuser:
            return True

        return hasattr(user, 'technician_profile')


class IsCompanyAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if user.is_staff or user.is_superuser:
            return True
        if hasattr(user, 'technician_profile'):
            return user.technician_profile.is_admin
        return False


class IsTicketAssigneeOrAdmin(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False

        profile = getattr(request.user, 'technician_profile', None)
        if not profile:
            return False

        if profile.is_admin:
            return True

        return obj.assigned_technician == profile

class ManageCompanyView(generics.RetrieveUpdateAPIView):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [IsAuthenticated, IsCompanyMember]

    def get_object(self):
        technician_profile = self.request.user.technician_profile
        return technician_profile.company



class UserProfileView(generics.RetrieveAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        # Zawsze zwracaj obiekt zalogowanego użytkownika
        return self.request.user

class RegisterView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        # Zwracamy dane nowo utworzonego użytkownika
        return Response(
            CustomUserSerializer(instance=user, context=self.get_serializer_context()).data,
            status=status.HTTP_201_CREATED
        )

class CompanyScopedViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, IsCompanyMember]

    def get_company(self):
        return self.request.user.technician_profile.company

    def get_queryset(self):
        return self.model.objects.filter(company=self.get_company())

    def perform_create(self, serializer):
        serializer.save(company=self.get_company())


class TechnicianViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, IsCompanyAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active', 'role']
    search_fields = ['user__first_name', 'user__last_name', 'user__email', 'user__username']
    ordering_fields = ['user__first_name', 'user__last_name', 'role']
    ordering = ['user__first_name']

    def get_queryset(self):
        company = self.request.user.technician_profile.company
        return Technician.objects.select_related('user').filter(company=company)

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return TechnicianWriteSerializer
        return TechnicianReadSerializer

    @action(detail=True, methods=['get'])
    def stats(self, request, pk=None):
        technician = self.get_object()
        today = timezone.now().date()

        assigned_tickets_count = ServiceTicket.objects.filter(
            assigned_technician=technician
        ).count()

        open_tickets_count = ServiceTicket.objects.filter(
            assigned_technician=technician,
            status=ServiceTicket.Status.OPEN
        ).count()

        in_progress_tickets_count = ServiceTicket.objects.filter(
            assigned_technician=technician,
            status=ServiceTicket.Status.IN_PROGRESS
        ).count()

        closed_tickets_count = ServiceTicket.objects.filter(
            assigned_technician=technician,
            status=ServiceTicket.Status.CLOSED
        ).count()

        valid_certifications_count = Certification.objects.filter(
            technician=technician,
            expiry_date__gte=today
        ).count()

        expiring_soon_count = Certification.objects.filter(
            technician=technician,
            expiry_date__gte=today,
            expiry_date__lte=today + timedelta(days=30)
        ).count()

        expired_certifications_count = Certification.objects.filter(
            technician=technician,
            expiry_date__lt=today
        ).count()

        return Response({
            'assigned_tickets_count': assigned_tickets_count,
            'open_tickets_count': open_tickets_count,
            'in_progress_tickets_count': in_progress_tickets_count,
            'closed_tickets_count': closed_tickets_count,
            'valid_certifications_count': valid_certifications_count,
            'expiring_soon_count': expiring_soon_count,
            'expired_certifications_count': expired_certifications_count,
        })


class ClientViewSet(CompanyScopedViewSet):
    permission_classes = [permissions.IsAuthenticated, IsCompanyAdmin]
    model = Client
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['nip']
    search_fields = ['name', 'nip', 'email']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']

    def get_serializer_class(self):
        if self.action == 'locations':
            return ClientLocationSerializer
        if self.action in ['create', 'update', 'partial_update']:
            return ClientWriteSerializer
        return ClientReadSerializer

    @action(detail=False, methods=['get'])
    def locations(self, request, *args, **kwargs):
        open_tickets_subquery = ServiceTicket.objects.filter(
            client=OuterRef('pk'),
            status=ServiceTicket.Status.OPEN
        )

        queryset = self.get_queryset().filter(
            latitude__isnull=False,
            longitude__isnull=False
        ).annotate(
            has_open_tickets=Exists(open_tickets_subquery)
        )

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], url_path='stats')
    def stats(self, request, pk=None):
        client = self.get_object()

        devices_count = FiscalDevice.objects.filter(owner=client).count()
        tickets_count = ServiceTicket.objects.filter(client=client).count()
        open_tickets_count = ServiceTicket.objects.filter(
            client=client,
            status=ServiceTicket.Status.OPEN
        ).count()

        return Response({
            'devices_count': devices_count,
            'tickets_count': tickets_count,
            'open_tickets_count': open_tickets_count,
        })


class ManufacturerViewSet(CompanyScopedViewSet):
    permission_classes = [permissions.IsAuthenticated, IsCompanyAdmin]
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
        return ManufacturerSummarySerializer

    def create(self, request, *args, **kwargs):
        write_serializer = self.get_serializer(data=request.data)
        write_serializer.is_valid(raise_exception=True)
        self.perform_create(write_serializer)

        instance = write_serializer.instance
        read_serializer = ManufacturerSummarySerializer(instance=instance, context=self.get_serializer_context())

        headers = self.get_success_headers(write_serializer.data)
        return Response(read_serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class CertificationViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, IsCompanyAdmin]
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

from django_filters import rest_framework as df_filters
from django_filters.rest_framework import DjangoFilterBackend

class NumberInFilter(df_filters.BaseInFilter, df_filters.NumberFilter):
    pass

class FiscalDeviceFilter(df_filters.FilterSet):
    owner__id__in = NumberInFilter(field_name='owner_id', lookup_expr='in')
    brand__id__in = NumberInFilter(field_name='brand_id', lookup_expr='in')

    class Meta:
        model = FiscalDevice
        fields = ['status', 'brand', 'owner__id__in', 'brand__id__in']


class FiscalDeviceViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, IsCompanyAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = FiscalDeviceFilter
    search_fields = ['model_name', 'serial_number', 'unique_number', 'owner__name']
    ordering = ['-sale_date']

    def get_queryset(self):
        company = self.request.user.technician_profile.company
        return FiscalDevice.objects.select_related('owner', 'brand').filter(
            owner__company=company
        ).prefetch_related('history_entries__actor').annotate(tickets_count=Count('tickets'))

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return FiscalDeviceWriteSerializer
        return FiscalDeviceReadSerializer

    def create(self, request, *args, **kwargs):
        write_serializer = self.get_serializer(data=request.data)
        write_serializer.is_valid(raise_exception=True)
        self.perform_create(write_serializer)

        instance = write_serializer.instance
        read_serializer = FiscalDeviceReadSerializer(instance=instance, context=self.get_serializer_context())

        headers = self.get_success_headers(write_serializer.data)
        return Response(read_serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=True, methods=['get'], url_path='eligible-technicians')
    def eligible_technicians(self, request, pk=None):
        device = self.get_object()
        company = request.user.technician_profile.company
        today = timezone.now().date()

        eligible_techs = Technician.objects.filter(
            company=company,
            is_active=True,
            certifications__manufacturer=device.brand,
            certifications__expiry_date__gte=today
        ).distinct()  # distinct() jest ważne, jeśli serwisant miałby kilka ważnych certyfikatów tej samej marki

        serializer = TechnicianSummarySerializer(eligible_techs, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsCompanyAdmin])
    def remind(self, request, pk=None):
        try:
            device = self.get_object()
        except FiscalDevice.DoesNotExist:
            return Response({"detail": "Urządzenie nie istnieje."}, status=status.HTTP_404_NOT_FOUND)

        if not getattr(device.owner, 'email', None):
            return Response({"detail": "Klient przypisany do tego urządzenia nie ma adresu email."},
                            status=status.HTTP_400_BAD_REQUEST)

        from api.tasks import send_device_inspection_reminder

        send_device_inspection_reminder.delay(device_id=device.id)

        if hasattr(device, 'last_reminder_sent'):
            device.last_reminder_sent = timezone.now()
            device.reminder_count = (getattr(device, 'reminder_count', 0) or 0) + 1
            device.save(update_fields=['last_reminder_sent', 'reminder_count'])

        return Response({"detail": f"Zlecono wysłanie przypomnienia dla urządzenia {device.unique_number}."},
                        status=status.HTTP_202_ACCEPTED)

    @action(detail=False, methods=['post'], url_path='send-reminders',
            permission_classes=[IsAuthenticated, IsCompanyAdmin])
    def send_reminders(self, request):
        device_ids = request.data.get('device_ids')

        if not isinstance(device_ids, list) or not device_ids:
            return Response({"detail": "Oczekiwano listy ID urządzeń w polu 'device_ids'."},
                            status=status.HTTP_400_BAD_REQUEST)

        company = request.user.technician_profile.company
        devices = FiscalDevice.objects.filter(
            id__in=device_ids,
            owner__company=company
        )

        sent_count = 0
        skipped_no_email = []

        from api.tasks import send_device_inspection_reminder

        for device in devices:
            if getattr(device.owner, 'email', None):
                send_device_inspection_reminder.delay(device_id=device.id)
                sent_count += 1
            else:
                skipped_no_email.append(device.unique_number or device.id)

        response_data = {
            "detail": f"Zlecono wysłanie {sent_count} przypomnień.",
            "sent_count": sent_count,
            "skipped_no_email": skipped_no_email
        }
        return Response(response_data, status=status.HTTP_202_ACCEPTED)

    @action(detail=True, methods=['post'], url_path='perform-service')
    def perform_service(self, request, pk=None):
        device = self.get_object()
        technician_id = request.data.get('technician_id')
        today = timezone.now().date()

        if not technician_id:
            return Response({"detail": "Należy wybrać serwisanta."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            technician = Technician.objects.get(
                id=technician_id,
                company=request.user.technician_profile.company
            )

            has_valid_certification = technician.certifications.filter(
                manufacturer=device.brand,
                expiry_date__gte=today
            ).exists()

            if not has_valid_certification:
                return Response({"detail": "Wybrany serwisant nie ma ważnych uprawnień dla tej marki urządzenia."},
                                status=status.HTTP_403_FORBIDDEN)

        except Technician.DoesNotExist:
            return Response({"detail": "Wybrany serwisant nie istnieje."}, status=status.HTTP_404_NOT_FOUND)

        with transaction.atomic():
            device.last_service_date = today
            device.save(update_fields=['last_service_date'])

            DeviceHistoryEntry.objects.create(
                device=device,
                action_type=DeviceHistoryEntry.ActionType.SERVICE_PERFORMED,
                description=f"Wykonano okresowy przegląd urządzenia. Wykonawca: {technician.full_name}.",
                actor=technician.user if technician.user else request.user
            )

        serializer = self.get_serializer(instance=device)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ServiceTicketViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, IsCompanyMember]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'ticket_type', 'assigned_technician', 'client', 'device']
    search_fields = ['ticket_number', 'title', 'description', 'client__name']
    ordering = ['-created_at']

    def get_queryset(self):
        user = self.request.user
        company = user.technician_profile.company

        if user.technician_profile.is_admin:
            return ServiceTicket.objects.filter(client__company=company).select_related(
                'client', 'device', 'assigned_technician'
            )
        return ServiceTicket.objects.filter(
            client__company=company,
            assigned_technician=user.technician_profile
        ).select_related('client', 'device', 'assigned_technician')

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy', 'resolve']:
            return [permissions.IsAuthenticated(), IsTicketAssigneeOrAdmin()]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == 'resolve':
            return ServiceTicketResolveSerializer

        if self.action in ['create', 'update']:
            return ServiceTicketWriteSerializer

        if self.action == 'partial_update':
            if list(self.request.data.keys()) == ['status']:
                return ServiceTicketTechnicianUpdateSerializer  # Ten serializer zawiera 'status'

            if self.request.user.technician_profile.is_admin:
                return ServiceTicketWriteSerializer

            return ServiceTicketTechnicianUpdateSerializer

        return ServiceTicketReadSerializer

    def perform_create(self, serializer):
        serializer.save()

    def create(self, request, *args, **kwargs):
        write_serializer = self.get_serializer(data=request.data)
        write_serializer.is_valid(raise_exception=True)
        self.perform_create(write_serializer)

        instance = write_serializer.instance
        read_serializer = ServiceTicketReadSerializer(instance=instance, context=self.get_serializer_context())

        headers = self.get_success_headers(write_serializer.data)
        return Response(read_serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=True, methods=['post'], url_path='resolve')
    def resolve(self, request, pk=None):
        ticket = self.get_object()

        if ticket.status == ServiceTicket.Status.CLOSED:
            return Response(
                {"detail": "To zgłoszenie jest już zamknięte."},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            ticket.resolution = serializer.validated_data['resolution']
            ticket.resolution_notes = serializer.validated_data.get('resolution_notes', ticket.resolution_notes)
            ticket.status = ServiceTicket.Status.CLOSED
            ticket.completed_at = timezone.now()
            ticket.save()

            if ticket.device:
                DeviceHistoryEntry.objects.create(
                    device=ticket.device,
                    action_type=DeviceHistoryEntry.ActionType.TICKET_COMPLETED,
                    description=f"Zakończono zlecenie serwisowe nr {ticket.ticket_number} ('{ticket.title}'). Wynik: {ticket.get_resolution_display()}.",
                    actor=request.user
                )

        return Response(ServiceTicketReadSerializer(instance=ticket).data, status=status.HTTP_200_OK)



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

import traceback
import logging

logger = logging.getLogger(__name__)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_checkout_session(request):
    try:
        print("✅ create_checkout_session HIT", flush=True)
        print("user:", getattr(request.user, "id", None), getattr(request.user, "email", None), flush=True)
        print("data:", request.data, flush=True)

        stripe.api_key = settings.STRIPE_SECRET_KEY

        user = request.user
        if hasattr(user, 'technician_profile'):
            return Response(
                {'error': 'Twoje konto jest już aktywne i nie możesz rozpocząć nowej sesji płatności.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        email = user.email or ''
        amount_cents = request.data.get('amount_cents')

        order = Order.objects.create(
            company=None,
            email=email,
            status='pending',
            amount_cents=amount_cents or None,
            currency='PLN',
        )

        metadata = {
            'order_id': str(order.id),
            'requested_by_user_id': str(user.id),
        }

        if getattr(settings, 'STRIPE_PRICE_ID', None):
            session = stripe.checkout.Session.create(
                mode='payment',
                line_items=[{'price': settings.STRIPE_PRICE_ID, 'quantity': 1}],
                success_url=f"{settings.FRONTEND_URL}/payment/success?session_id={{CHECKOUT_SESSION_ID}}",
                cancel_url=f"{settings.FRONTEND_URL}/payment/cancel",
                metadata=metadata,
                customer_email=email or None,
            )
        else:
            if not amount_cents:
                order.delete()
                return Response(
                    {'error': 'No amount provided and no STRIPE_PRICE_ID configured.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            session = stripe.checkout.Session.create(
                mode='payment',
                line_items=[{
                    'price_data': {
                        'currency': 'pln',
                        'product_data': {'name': 'Abonament'},
                        'unit_amount': int(amount_cents)
                    },
                    'quantity': 1
                }],
                success_url=f"{settings.FRONTEND_URL}/payment/success?session_id={{CHECKOUT_SESSION_ID}}",
                cancel_url=f"{settings.FRONTEND_URL}/payment/cancel",
                metadata=metadata,
                customer_email=email or None,
            )

        order.stripe_session_id = session.id
        order.save(update_fields=['stripe_session_id'])

        return Response({'sessionId': session.id, 'url': session.url, 'orderId': str(order.id)})


    except Exception as e:
        tb = traceback.format_exc()
        print("🔥 create_checkout_session ERROR:", str(e), flush=True)
        print(tb, flush=True)
        logger.exception("create_checkout_session failed")

        try:
            if 'order' in locals() and order:
                order.status = 'failed'
                order.save(update_fields=['status'])
        except Exception:
            pass

        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def handle_payment_success(request):
    session_id = request.data.get('session_id')
    if not session_id:
        return Response({'error': 'Brak session_id'}, status=status.HTTP_400_BAD_REQUEST)

    stripe.api_key = settings.STRIPE_SECRET_KEY
    try:
        session = stripe.checkout.Session.retrieve(session_id)
        if session.get('payment_status') != 'paid':
            return Response(
                {'status': 'pending', 'message': 'Płatność nie została jeszcze potwierdzona.'},
                status=status.HTTP_202_ACCEPTED
            )

        order = Order.objects.filter(stripe_session_id=session.id).first()
        if not order or order.status != 'paid':
            return Response(
                {'status': 'processing', 'message': 'Płatność jest przetwarzana. Spróbuj ponownie za chwilę.'},
                status=status.HTTP_202_ACCEPTED
            )

        activation = ActivationCode.objects.filter(order=order).first()
        if not activation:
            # To oznacza, że webhook go jeszcze nie utworzył
            return Response(
                {'status': 'processing', 'message': 'Kod aktywacyjny jest w trakcie generowania.'},
                status=status.HTTP_202_ACCEPTED
            )

        return Response({'code': activation.code}, status=status.HTTP_200_OK)

    except stripe.error.StripeError as e:
        return Response({'error': f'Błąd Stripe: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@csrf_exempt
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def stripe_webhook(request):
    try:
        print("✅ stripe_webhook HIT", flush=True)
        print("len(payload):", len(request.body or b""), flush=True)
        print("sig header present:", bool(request.META.get("HTTP_STRIPE_SIGNATURE")), flush=True)

        stripe.api_key = settings.STRIPE_SECRET_KEY
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE', '')
        endpoint_secret = getattr(settings, 'STRIPE_WEBHOOK_SECRET', None)

        if not endpoint_secret:
            return Response({'error': 'Webhook secret not configured'}, status=500)

        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)

        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            metadata = session.get('metadata') or {}
            order_id_from_meta = metadata.get('order_id')

            with transaction.atomic():
                if order_id_from_meta:
                    order, _ = Order.objects.get_or_create(
                        id=order_id_from_meta,
                        defaults={
                            'company': None,
                            'email': session.get('customer_details', {}).get('email', ''),
                            'status': 'pending',
                            'stripe_session_id': session.id,
                        }
                    )
                else:
                    order, _ = Order.objects.get_or_create(
                        stripe_session_id=session.id,
                        defaults={
                            'company': None,
                            'email': session.get('customer_details', {}).get('email', ''),
                            'status': 'pending',
                        }
                    )

                order.status = 'paid'
                order.amount_cents = session.get('amount_total', order.amount_cents or 0)
                order.currency = (session.get('currency') or order.currency or 'pln').upper()
                order.stripe_payment_intent = session.get('payment_intent')
                order.save()

                ActivationCode.objects.get_or_create(order=order, defaults={'email': order.email})

        return Response({'status': 'success'}, status=200)

    except Exception as e:
        tb = traceback.format_exc()
        print("🔥 stripe_webhook ERROR:", str(e), flush=True)
        print(tb, flush=True)
        logger.exception("stripe_webhook failed")
        return Response({'error': 'webhook failed'}, status=500)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_activation_codes(request):
    user_email = request.user.email
    qs = ActivationCode.objects.select_related('order__company', 'used_by').filter(order__email=user_email)
    serializer = ActivationCodeReadSerializer(qs, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def redeem_activation_code(request):
    code_value = request.data.get('code')
    if not code_value:
        return Response({'error': 'Brak kodu'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        activation = ActivationCode.objects.select_related('order__company').get(code=code_value)
    except ActivationCode.DoesNotExist:
        return Response({'error': 'Nieprawidłowy kod'}, status=status.HTTP_404_NOT_FOUND)

    if activation.used:
        return Response({'error': 'Kod został już użyty'}, status=status.HTTP_400_BAD_REQUEST)
    if hasattr(request.user, 'technician_profile'):
        return Response({'error': 'Twoje konto jest już powiązane z firmą.'}, status=status.HTTP_400_BAD_REQUEST)
    if activation.order.status != 'paid':
        return Response({'error': 'Zamówienie powiązane z tym kodem nie jest jeszcze opłacone.'},
                        status=status.HTTP_400_BAD_REQUEST)

    with transaction.atomic():
        order = activation.order
        company = order.company

        is_first_user = company is None

        if not company:
            company_name = f"Firma {order.email or request.user.email}"
            company = Company.objects.create(name=company_name)

            order.company = company
            order.save(update_fields=['company'])

        technician = Technician.objects.create(
            user=request.user,
            company=company,
            first_name=request.user.first_name or '',
            last_name=request.user.last_name or '',
            email=request.user.email or '',
            is_active=True,
            role=Technician.ROLE_ADMIN if is_first_user else Technician.ROLE_TECHNICIAN
        )

        activation.redeem(request.user)

    request.user.refresh_from_db()
    user_data = UserProfileSerializer(instance=request.user, context={'request': request}).data

    return Response({
        'detail': 'Kod zrealizowany! Twoje konto jest teraz w pełni aktywne.',
        'user': user_data
    }, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsCompanyAdmin]) # Tylko admin może generować raporty
def export_device_pdf(request, device_id):
    try:
        company = request.user.technician_profile.company

        device = FiscalDevice.objects.select_related(
            'owner',
            'brand'
        ).prefetch_related(
            'tickets__assigned_technician',
            'history_entries__actor'
        ).get(
            id=device_id,
            owner__company=company
        )
    except FiscalDevice.DoesNotExist:
        return Response({'error': 'Nie znaleziono urządzenia.'}, status=status.HTTP_404_NOT_FOUND)

    context = {
        'device': device,
        'generation_date': timezone.now().strftime('%Y-%m-%d %H:%M:%S')
    }

    html_string = render_to_string('device_report.html', context)
    pdf_file = HTML(string=html_string).write_pdf()

    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="raport_urzadzenia_{device.unique_number}.pdf"'

    return response

from django.db.models import Count
from django.db.models.functions import TruncMonth


class ChartView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsCompanyMember]

    def get(self, request, *args, **kwargs):
        company = request.user.technician_profile.company

        tickets_by_status_qs = ServiceTicket.objects.filter(
            client__company=company
        ).values('status').annotate(count=Count('id')).order_by('status')
        status_labels_map = dict(ServiceTicket.Status.choices)
        tickets_by_status_data = {
            "labels": [status_labels_map.get(item['status'], item['status']) for item in tickets_by_status_qs],
            "data": [item['count'] for item in tickets_by_status_qs]
        }

        twelve_months_ago = timezone.now().date() - relativedelta(months=11)
        twelve_months_ago = twelve_months_ago.replace(day=1)

        tickets_by_month_and_type = ServiceTicket.objects.filter(
            client__company=company,
            created_at__gte=twelve_months_ago
        ).annotate(
            month=TruncMonth('created_at')
        ).values('month', 'ticket_type').annotate(count=Count('id')).order_by('month')

        monthly_data = defaultdict(lambda: defaultdict(int))
        for item in tickets_by_month_and_type:
            month_str = item['month'].strftime('%Y-%m')
            monthly_data[month_str][item['ticket_type']] += item['count']

        all_months_labels = []
        today = date.today()
        for i in range(12, 0, -1):
            month_date = today - relativedelta(months=i - 1)
            all_months_labels.append(month_date.strftime('%Y-%m'))

        colors = {
            ServiceTicket.TicketType.SERVICE: {'bg': 'rgba(75, 192, 192, 0.7)', 'border': 'rgb(75, 192, 192)'},
            ServiceTicket.TicketType.REPAIR: {'bg': 'rgba(255, 99, 132, 0.7)', 'border': 'rgb(255, 99, 132)'},
            ServiceTicket.TicketType.READING: {'bg': 'rgba(54, 162, 235, 0.7)', 'border': 'rgb(54, 162, 235)'},
            ServiceTicket.TicketType.OTHER: {'bg': 'rgba(201, 203, 207, 0.7)', 'border': 'rgb(201, 203, 207)'},
        }

        datasets = []
        for ticket_type_value, ticket_type_label in ServiceTicket.TicketType.choices:
            data_for_all_months = [monthly_data[month].get(ticket_type_value, 0) for month in all_months_labels]
            color_set = colors.get(ticket_type_value)  # Bezpieczne pobranie

            dataset = {
                "label": ticket_type_label,
                "data": data_for_all_months,
                "backgroundColor": color_set['bg'],
                "borderColor": color_set['border'],
            }
            datasets.append(dataset)

        workload_over_time_data = {
            "labels": [datetime.strptime(m, '%Y-%m').strftime('%B %Y') for m in all_months_labels],
            "datasets": datasets
        }

        devices_by_status_qs = FiscalDevice.objects.filter(
            owner__company=company
        ).values('status').annotate(count=Count('id')).order_by('status')
        device_status_map = dict(FiscalDevice.Status.choices)
        devices_by_status_data = {
            "labels": [device_status_map.get(item['status'], item['status']) for item in devices_by_status_qs],
            "data": [item['count'] for item in devices_by_status_qs]
        }

        ninety_days_from_now = timezone.now().date() + timedelta(days=90)
        expiring_certs_qs = Certification.objects.filter(
            technician__company=company,
            expiry_date__lte=ninety_days_from_now,
            expiry_date__gte=timezone.now().date()
        ).select_related('technician__user', 'manufacturer').order_by('expiry_date')
        expiring_certs_data = [
            {
                "technician": cert.technician.full_name,
                "manufacturer": cert.manufacturer.name,
                "certificate_number": cert.certificate_number,
                "expiry_date": cert.expiry_date.strftime('%Y-%m-%d'),
            } for cert in expiring_certs_qs
        ]

        response_data = {
            "tickets_by_status": tickets_by_status_data,
            "workload_over_time": workload_over_time_data,
            "devices_by_status": devices_by_status_data,
            "expiring_certifications": expiring_certs_data,
        }
        return Response(response_data, status=status.HTTP_200_OK)


class CSVRenderer(BaseRenderer):
    media_type = 'text/csv'
    format = 'csv'
    charset = 'utf-8'

    def render(self, data, media_type=None, renderer_context=None):
        if not data:
            return ""

        if not isinstance(data, list) or not isinstance(data[0], dict):
            return JSONRenderer().render(data, media_type, renderer_context)

        headers = data[0].keys()

        from io import StringIO
        string_buffer = StringIO()
        writer = csv.DictWriter(string_buffer, fieldnames=headers)

        writer.writeheader()
        writer.writerows(data)

        return string_buffer.getvalue().encode(self.charset)


class ReportFilterOptionsView(APIView):
    permission_classes = [IsAuthenticated, IsCompanyAdmin]

    def get(self, request, *args, **kwargs):
        company = request.user.technician_profile.company

        clients = Client.objects.filter(company=company).values('id', 'name')
        technicians = Technician.objects.filter(company=company).values('id', 'first_name', 'last_name')
        brands = Manufacturer.objects.filter(company=company).values('id', 'name')

        return Response({
            'clients': list(clients),
            'technicians': [{'id': t['id'], 'name': f"{t['first_name']} {t['last_name']}"} for t in technicians],
            'brands': list(brands),
            'ticket_statuses': [{'value': choice[0], 'text': choice[1]} for choice in ServiceTicket.Status.choices],
            'ticket_types': [{'value': choice[0], 'text': choice[1]} for choice in ServiceTicket.TicketType.choices],
            'ticket_resolutions': [{'value': choice[0], 'text': choice[1]} for choice in
                                   ServiceTicket.Resolution.choices],
        })

from django.db.models import Prefetch


class GenerateReportView(APIView):
    permission_classes = [IsAuthenticated, IsCompanyAdmin]
    renderer_classes = [JSONRenderer]

    def post(self, request, *args, **kwargs):
        serializer = ReportParameterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        params = serializer.validated_data
        company = request.user.technician_profile.company

        queryset = FiscalDevice.objects.filter(owner__company=company)

        if params.get('clients'):
            queryset = queryset.filter(owner_id__in=params['clients'])
        if params.get('devices'):
            queryset = queryset.filter(id__in=params['devices'])
        if params.get('device_brands'):
            queryset = queryset.filter(brand_id__in=params['device_brands'])

        prefetch_list = [
            'owner',
            'brand'
        ]

        if params.get('include_service_history'):
            tickets_queryset = ServiceTicket.objects.select_related('assigned_technician').order_by('-created_at')
            if params.get('history_date_from'):
                tickets_queryset = tickets_queryset.filter(created_at__date__gte=params['history_date_from'])
            if params.get('history_date_to'):
                tickets_queryset = tickets_queryset.filter(created_at__date__lte=params['history_date_to'])

            prefetch_list.append(
                Prefetch('tickets', queryset=tickets_queryset, to_attr='filtered_tickets')
            )

        if params.get('include_event_log'):
            prefetch_list.append(Prefetch('history_entries',
                                          queryset=DeviceHistoryEntry.objects.select_related('actor').order_by(
                                              '-event_date')))

        devices = queryset.prefetch_related(*prefetch_list).order_by('owner__name', 'model_name')

        output_format = params.get('output_format', 'json')

        if output_format == 'pdf':
            context = {
                'devices': devices,
                'params': params,
                'generation_date': timezone.now().strftime('%Y-%m-%d %H:%M:%S'),
                'company_name': company.name
            }
            html_string = render_to_string('reports/generic_report.html', context)
            pdf_file = HTML(string=html_string, base_url=request.build_absolute_uri()).write_pdf()

            response = HttpResponse(pdf_file, content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="raport_zbiorczy_urzadzen.pdf"'
            return response

        report_data = FiscalDeviceReadSerializer(devices, many=True).data
        return Response(report_data)

from .tasks import send_email_task

class RequestEmailChangeView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ChangeEmailSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        new_email = serializer.validated_data['new_email']
        password = serializer.validated_data['password']

        if not user.check_password(password):
            return Response({"error": "Nieprawidłowe hasło."}, status=status.HTTP_400_BAD_REQUEST)

        signer = TimestampSigner()
        payload = {
            'user_id': user.id,
            'new_email': new_email
        }
        token = signer.sign_object(payload)

        confirm_url = f"{settings.FRONTEND_URL}/settings/confirm-email-change?token={token}"

        context = {
            'username': user.username,
            'confirm_url': confirm_url,
        }

        subject = "Potwierdź zmianę adresu e-mail w aplikacji Serwisant"
        html_message = render_to_string('emails/confirm_email_change.html', context)
        plain_message = render_to_string('emails/confirm_email_change.txt', context)

        send_email_task.delay(
            subject=subject,
            body=plain_message,
            to_email=new_email,  # Wyślij na NOWY adres
            html_body=html_message
        )

        return Response(
            {"detail": f"Link potwierdzający został wysłany na adres {new_email}."},
            status=status.HTTP_200_OK
        )


class ConfirmEmailChangeView(APIView):
    permission_classes = [permissions.AllowAny]  # Każdy z linkiem może tu wejść
    serializer_class = ConfirmEmailChangeSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.validated_data['token']

        signer = TimestampSigner()
        try:
            payload = signer.unsign_object(token, max_age=3600)
            user_id = payload['user_id']
            new_email = payload['new_email']

            user = CustomUser.objects.get(id=user_id)

            if CustomUser.objects.filter(email__iexact=new_email).exclude(id=user_id).exists():
                return Response({"error": "Ten adres e-mail został w międzyczasie zajęty."},
                                status=status.HTTP_400_BAD_REQUEST)

            user.email = new_email
            user.save(update_fields=['email'])

            if hasattr(user, 'technician_profile'):
                user.technician_profile.email = new_email
                user.technician_profile.save(update_fields=['email'])

            return Response({"detail": "Adres e-mail został pomyślnie zmieniony."}, status=status.HTTP_200_OK)

        except SignatureExpired:
            return Response({"error": "Link potwierdzający wygasł."}, status=status.HTTP_400_BAD_REQUEST)
        except BadSignature:
            return Response({"error": "Nieprawidłowy link potwierdzający."}, status=status.HTTP_400_BAD_REQUEST)
        except CustomUser.DoesNotExist:
            return Response({"error": "Użytkownik nie istnieje."}, status=status.HTTP_404_NOT_FOUND)


class GetAiSuggestionView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsCompanyMember]
    serializer_class = AiSuggestionRequestSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        description = serializer.validated_data['description']

        try:
            genai.configure(api_key=settings.GOOGLE_API_KEY)
        except Exception as e:
            return Response({"error": f"Błąd konfiguracji Google AI: {e}"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        full_prompt = f"""
        Twoim zadaniem jest analiza opisu problemu z urządzeniem fiskalnym i zwrócenie odpowiedzi WYŁĄCZNIE w formacie JSON.
        Nie dodawaj żadnych dodatkowych wyjaśnień, komentarzy ani tekstu poza obiektem JSON. Nie używaj znaczników markdown takich jak ```json.

        Opis problemu: "{description}"

        Zwróć obiekt JSON zawierający następujące klucze:
        - "possible_cause": (string) Krótki, prawdopodobny powód problemu.
        - "suggested_category": (string) Jedna z wartości: "Sprzęt", "Oprogramowanie", "Sieć", "Użytkownik", "Inne".
        - "diagnostic_steps": (array of strings) Lista 3-5 konkretnych kroków diagnostycznych do wykonania.
        """

        try:
            model = genai.GenerativeModel('gemini-2.5-flash-lite')

            generation_config = genai.types.GenerationConfig(
                response_mime_type="application/json"
            )

            response = model.generate_content(
                full_prompt,
                generation_config=generation_config
            )

            suggestions = json.loads(response.text)
            return Response(suggestions, status=status.HTTP_200_OK)

        except Exception as e:
            error_message = f"Błąd podczas komunikacji z Google Gemini API: {e}"
            print(error_message)

            if "API key not valid" in str(e):
                error_message = "Klucz API do Google AI jest nieprawidłowy lub wygasł."
            elif "404" in str(e) and "is not found" in str(e):
                error_message = "Wybrany model AI nie jest dostępny. Skontaktuj się z administratorem."
            else:
                error_message = "Wystąpił błąd po stronie serwera AI. Spróbuj ponownie później."

            return Response({"error": error_message}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

from .serializers import UserProfileUpdateSerializer
class UpdateUserProfileView(generics.UpdateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserProfileUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(UserProfileSerializer(instance, context={'request': request}).data)