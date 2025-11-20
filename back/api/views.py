from collections import defaultdict
from datetime import timedelta, datetime
import stripe
import requests
from django.conf import settings
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt

from django.db.models import Count
from django.utils import timezone
from rest_framework import viewsets, generics, permissions, status, filters
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated

from .models.users import Technician, Company, CustomUser
from .models.clients import Client
from .models.manufacturers import Manufacturer, Certification
from .models.devices import FiscalDevice
from .models.tickets import ServiceTicket
from .models.billing import Order, ActivationCode

from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML

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
    ServiceTicketTechnicianUpdateSerializer, ServiceTicketResolveSerializer
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
        user = request.user
        if not user or not user.is_authenticated:
            return False

        if user.is_superuser:
            return True

        return hasattr(user, 'technician_profile')


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
            return user.technician_profile.is_admin
        return False


class IsTicketAssigneeOrAdmin(permissions.BasePermission):
    """Zezwala na dostęp do obiektu, jeśli użytkownik jest adminem lub przypisanym serwisantem."""

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
    """
    Widok do pobierania (GET) i aktualizowania (PUT/PATCH)
    danych firmy, do której należy zalogowany użytkownik.
    """
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [IsAuthenticated, IsCompanyMember] # Tylko członek firmy ma dostęp

    def get_object(self):
        """
        Zwraca obiekt firmy powiązany z zalogowanym użytkownikiem.
        """
        # Pobieramy profil technika zalogowanego użytkownika
        technician_profile = self.request.user.technician_profile
        # Zwracamy firmę tego technika
        return technician_profile.company



class UserProfileView(generics.RetrieveAPIView):
    """
    Widok do pobierania danych zalogowanego użytkownika.
    Zwraca dane zgodne z typem UserProfile na frontendzie.
    """
    queryset = CustomUser.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        # Zawsze zwracaj obiekt zalogowanego użytkownika
        return self.request.user
# -------------------------
# Registration
# -------------------------

class RegisterView(generics.CreateAPIView):
    """
    Prosty endpoint do rejestracji użytkownika.
    Tworzy tylko obiekt CustomUser bez żadnych dodatkowych uprawnień czy profili.
    """
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


# -------------------------
# Clients, Manufacturers (używają teraz CompanyScopedViewSet)
# -------------------------

class ClientViewSet(CompanyScopedViewSet):
    permission_classes = [permissions.IsAuthenticated, IsCompanyAdmin]
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
        return ManufacturerSummarySerializer  # lub pełny ReadSerializer jeśli istnieje

    def create(self, request, *args, **kwargs):
        """
        Nadpisana metoda create, aby użyć innego serializera dla odpowiedzi.
        """
        # 1. Użyj serializera do zapisu (Write) do walidacji i utworzenia obiektu
        write_serializer = self.get_serializer(data=request.data)
        write_serializer.is_valid(raise_exception=True)
        self.perform_create(write_serializer)

        # 2. Utwórz odpowiedź używając serializera do odczytu (Read)
        # Pobieramy nowo utworzoną instancję
        instance = write_serializer.instance
        # Tworzymy serializer do odczytu na tej instancji
        read_serializer = ManufacturerSummarySerializer(instance=instance, context=self.get_serializer_context())

        headers = self.get_success_headers(write_serializer.data)
        return Response(read_serializer.data, status=status.HTTP_201_CREATED, headers=headers)


# -------------------------
# Certifications, Devices, Tickets (wymagają bardziej złożonego filtrowania)
# -------------------------

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


class FiscalDeviceViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, IsCompanyAdmin]
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

    def create(self, request, *args, **kwargs):
        """
        Nadpisana metoda create, aby zwrócić pełne dane obiektu
        używając serializera do odczytu (FiscalDeviceReadSerializer).
        """
        write_serializer = self.get_serializer(data=request.data)
        write_serializer.is_valid(raise_exception=True)
        self.perform_create(write_serializer)

        instance = write_serializer.instance
        read_serializer = FiscalDeviceReadSerializer(instance=instance, context=self.get_serializer_context())

        headers = self.get_success_headers(write_serializer.data)
        return Response(read_serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsCompanyAdmin])
    def remind(self, request, pk=None):
        """
        Uruchamia wysyłkę emaila z przypomnieniem o przeglądzie dla JEDNEGO urządzenia.
        """
        try:
            device = self.get_object()
        except FiscalDevice.DoesNotExist:
            return Response({"detail": "Urządzenie nie istnieje."}, status=status.HTTP_404_NOT_FOUND)

        if not getattr(device.owner, 'email', None):
            return Response({"detail": "Klient przypisany do tego urządzenia nie ma adresu email."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Import zadania Celery
        from api.tasks import send_device_inspection_reminder

        # Wywołujemy zadanie z poprawnym argumentem (tylko device_id)
        send_device_inspection_reminder.delay(device_id=device.id)

        # Zaktualizujmy pola last_reminder_sent i reminder_count natychmiast,
        # aby użytkownik widział efekt od razu w UI (opcjonalne, ale dobra praktyka)
        # UWAGA: Model FiscalDevice musi mieć te pola. Widzę, że masz je w modelu Inspection,
        # więc upewnij się, że FiscalDevice też je ma, lub zignoruj tę część.
        # Zakładając, że ma:
        if hasattr(device, 'last_reminder_sent'):
            device.last_reminder_sent = timezone.now()
            device.reminder_count = (getattr(device, 'reminder_count', 0) or 0) + 1
            device.save(update_fields=['last_reminder_sent', 'reminder_count'])

        return Response({"detail": f"Zlecono wysłanie przypomnienia dla urządzenia {device.unique_number}."},
                        status=status.HTTP_202_ACCEPTED)

    # NOWA AKCJA dla wielu urządzeń
    @action(detail=False, methods=['post'], url_path='send-reminders',
            permission_classes=[IsAuthenticated, IsCompanyAdmin])
    def send_reminders(self, request):
        """
        Uruchamia wysyłkę emaili z przypomnieniem dla listy urządzeń.
        Oczekuje w ciele zapytania: { "device_ids": [1, 2, 3] }
        """
        device_ids = request.data.get('device_ids')

        if not isinstance(device_ids, list) or not device_ids:
            return Response({"detail": "Oczekiwano listy ID urządzeń w polu 'device_ids'."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Pobierz urządzenia należące do firmy użytkownika, żeby nikt nie wysłał maili dla cudzych urządzeń
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
        """
        Ustawia datę ostatniego przeglądu ('last_service_date') na dzisiejszą.
        """
        try:
            # Użyj get_object(), aby skorzystać z domyślnego filtrowania uprawnień
            device = self.get_object()
        except FiscalDevice.DoesNotExist:
            return Response({"detail": "Urządzenie nie istnieje."}, status=status.HTTP_404_NOT_FOUND)

        # Ustaw datę ostatniego przeglądu na dzisiaj
        device.last_service_date = timezone.now().date()
        device.save(update_fields=['last_service_date'])

        # Zwróć zaktualizowany obiekt urządzenia, aby frontend mógł odświeżyć dane
        # Użyj serializera do odczytu, który zawiera obliczone pole 'next_service_date'
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

        # Admin widzi wszystkie zgłoszenia w firmie
        if user.technician_profile.is_admin:
            return ServiceTicket.objects.filter(client__company=company).select_related(
                'client', 'device', 'assigned_technician'
            )
        # Zwykły serwisant widzi tylko swoje zgłoszenia
        return ServiceTicket.objects.filter(
            client__company=company,
            assigned_technician=user.technician_profile
        ).select_related('client', 'device', 'assigned_technician')

    def get_permissions(self):
        # POPRAWKA: Dodano 'resolve' do listy akcji wymagających uprawnień do obiektu
        if self.action in ['update', 'partial_update', 'destroy', 'resolve']:
            return [permissions.IsAuthenticated(), IsTicketAssigneeOrAdmin()]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == 'resolve':
            return ServiceTicketResolveSerializer

        # Dla akcji tworzenia i pełnej aktualizacji używamy pełnego serializera
        if self.action in ['create', 'update']:
            return ServiceTicketWriteSerializer

        # Dla PATCH (częściowa aktualizacja), czyli naszego drag-and-drop
        if self.action == 'partial_update':
            # Jeśli jedynym kluczem w zapytaniu jest 'status', to jest to operacja z Kanbana.
            # Używamy prostego serializera, który pozwala na zmianę statusu.
            if list(self.request.data.keys()) == ['status']:
                return ServiceTicketTechnicianUpdateSerializer  # Ten serializer zawiera 'status'

            # Jeśli admin wysyła bardziej złożony PATCH (np. z modala), użyj pełnego serializera
            if self.request.user.technician_profile.is_admin:
                return ServiceTicketWriteSerializer

            # W przeciwnym razie, dla zwykłego technika, użyj ograniczonego serializera
            return ServiceTicketTechnicianUpdateSerializer

        # Domyślnie dla 'list' i 'retrieve' używamy serializera do odczytu
        return ServiceTicketReadSerializer

    # POPRAWKA: Dodano brakującą metodę perform_create
    def perform_create(self, serializer):
        """
        Zapisuje nowe zgłoszenie. Jeśli model `ServiceTicket` ma specjalną logikę
        w metodzie `save()` (np. do generowania numeru), zostanie ona tutaj wywołana.
        """
        serializer.save()

    def create(self, request, *args, **kwargs):
        """
        Nadpisane, aby zwrócić pełne dane obiektu po utworzeniu, używając
        serializera do odczytu.
        """
        write_serializer = self.get_serializer(data=request.data)
        write_serializer.is_valid(raise_exception=True)
        self.perform_create(write_serializer)

        instance = write_serializer.instance
        read_serializer = ServiceTicketReadSerializer(instance=instance, context=self.get_serializer_context())

        headers = self.get_success_headers(write_serializer.data)
        return Response(read_serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=True, methods=['post'], url_path='resolve')
    def resolve(self, request, pk=None):
        """
        Oznacza zgłoszenie jako rozwiązane z podanym rezultatem i notatkami.
        Ta akcja ustawia główny status zgłoszenia na 'Zamknięte'.
        """
        ticket = self.get_object()

        if ticket.status == ServiceTicket.Status.CLOSED:
            return Response(
                {"detail": "To zgłoszenie jest już zamknięte."},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        ticket.resolution = serializer.validated_data['resolution']
        ticket.resolution_notes = serializer.validated_data.get('resolution_notes', ticket.resolution_notes)
        ticket.status = ServiceTicket.Status.CLOSED
        ticket.completed_at = timezone.now()
        ticket.save()

        # Zwracamy pełne, zaktualizowane dane zgłoszenia
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


# -------------------------
# Stripe payment endpoints
# -------------------------
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_checkout_session(request):
    """
    Tworzy lokalny Order (status 'pending') powiązany z zalogowanym użytkownikiem (email)
    i tworzy Stripe Checkout Session. Zwraca sessionId, url, orderId.
    Użytkownik musi być zalogowany (rejestracja przed zakupem).
    """
    stripe.api_key = settings.STRIPE_SECRET_KEY

    user = request.user
    if hasattr(user, 'technician_profile'):
        return Response(
            {'error': 'Twoje konto jest już aktywne i nie możesz rozpocząć nowej sesji płatności.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    email = user.email or ''
    amount_cents = request.data.get('amount_cents')  # opcjonalne, jeśli korzystasz z dynamicznych kwot

    # Pre-create Order w statusie pending
    order = Order.objects.create(
        company=None,  # firma będzie przypisana po przetworzeniu płatności (webhook) lub możesz przypisać inną logikę
        email=email,
        status='pending',
        amount_cents=amount_cents or None,
        currency='PLN',
    )

    try:
        # metadata do powiązania sesji z orderem i użytkownikiem
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
            # Jeśli chcesz dynamicznie ustawiać kwotę: wymagaj amount_cents
            if not amount_cents:
                order.delete()
                return Response({'error': 'No amount provided and no STRIPE_PRICE_ID configured.'}, status=status.HTTP_400_BAD_REQUEST)
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

        # zapisz stripe session id lokalnie (ułatwia dopasowanie)
        order.stripe_session_id = session.id
        order.save(update_fields=['stripe_session_id'])

        return Response({'sessionId': session.id, 'url': session.url, 'orderId': str(order.id)})

    except Exception as e:
        # w razie błędu oznacz order jako failed
        order.status = 'failed'
        order.save(update_fields=['status'])
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def handle_payment_success(request):
    """
    Sprawdza status płatności po stronie klienta.
    Nie tworzy żadnych danych, jedynie odpytuje istniejący stan.
    Głównym źródłem prawdy pozostaje webhook.
    """
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

        # Znajdź powiązane zamówienie
        order = Order.objects.filter(stripe_session_id=session.id).first()
        if not order or order.status != 'paid':
            # Jeśli order nie jest jeszcze 'paid', to znaczy, że webhook jeszcze nie dotarł.
            return Response(
                {'status': 'processing', 'message': 'Płatność jest przetwarzana. Spróbuj ponownie za chwilę.'},
                status=status.HTTP_202_ACCEPTED
            )

        # Znajdź kod aktywacyjny dla tego zamówienia
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
    """
    Webhook handler. Potwierdza płatność, aktualizuje/tworzy Order
    i tworzy powiązany z nim ActivationCode.
    Nie tworzy obiektu Company.
    """
    stripe.api_key = settings.STRIPE_SECRET_KEY
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE', '')
    endpoint_secret = getattr(settings, 'STRIPE_WEBHOOK_SECRET', None)

    if not endpoint_secret:
        return Response({'error': 'Webhook secret not configured'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except ValueError:
        return Response({'error': 'Invalid payload'}, status=status.HTTP_400_BAD_REQUEST)
    except stripe.error.SignatureVerificationError:
        return Response({'error': 'Invalid signature'}, status=status.HTTP_400_BAD_REQUEST)

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        metadata = session.get('metadata') or {}
        order_id_from_meta = metadata.get('order_id')

        try:
            with transaction.atomic():
                # Użyj get_or_create na podstawie order_id z metadanych Stripe,
                # a jeśli go nie ma, użyj session_id jako fallback
                if order_id_from_meta:
                    order, created = Order.objects.get_or_create(
                        id=order_id_from_meta,
                        defaults={
                            'company': None,
                            'email': session.get('customer_details', {}).get('email', ''),
                            'status': 'pending',
                            'stripe_session_id': session.id,
                        }
                    )
                else:
                    order, created = Order.objects.get_or_create(
                        stripe_session_id=session.id,
                        defaults={
                            'company': None,
                            'email': session.get('customer_details', {}).get('email', ''),
                            'status': 'pending',
                        }
                    )

                # Zawsze aktualizuj dane do stanu "opłacone"
                order.status = 'paid'
                order.amount_cents = session.get('amount_total', order.amount_cents or 0)
                order.currency = (session.get('currency') or order.currency or 'pln').upper()
                order.stripe_payment_intent = session.get('payment_intent')
                order.save()

                # Utwórz kod aktywacyjny, jeśli jeszcze nie istnieje
                # To jest bezpieczne, bo get_or_create jest atomowe
                ActivationCode.objects.get_or_create(
                    order=order,
                    defaults={'email': order.email}
                )
        except Exception as e:
            # TODO: Dodaj logowanie błędów do systemu monitoringu (np. Sentry)
            return Response({'error': f'Webhook processing error: {str(e)}'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response({'status': 'success'}, status=status.HTTP_200_OK)


# --- Endpoints dla użytkownika: sprawdzenie / realizacja kodu aktywacji ---

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_activation_codes(request):
    """
    Zwraca ActivationCode(y) powiązane z zalogowanym użytkownikiem (wg order.email).
    Przyjmujemy, że użytkownik kupił abonament używając jego email.
    """
    user_email = request.user.email
    qs = ActivationCode.objects.select_related('order__company', 'used_by').filter(order__email=user_email)
    serializer = ActivationCodeReadSerializer(qs, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def redeem_activation_code(request):
    """
    Realizuje kod aktywacyjny. Jeśli to pierwszy użytkownik dla danego zamówienia,
    tworzy nową firmę i przypisuje mu rolę admina.
    """
    code_value = request.data.get('code')
    if not code_value:
        return Response({'error': 'Brak kodu'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        activation = ActivationCode.objects.select_related('order__company').get(code=code_value)
    except ActivationCode.DoesNotExist:
        return Response({'error': 'Nieprawidłowy kod'}, status=status.HTTP_404_NOT_FOUND)

    # --- Walidacje ---
    if activation.used:
        return Response({'error': 'Kod został już użyty'}, status=status.HTTP_400_BAD_REQUEST)
    if hasattr(request.user, 'technician_profile'):
        return Response({'error': 'Twoje konto jest już powiązane z firmą.'}, status=status.HTTP_400_BAD_REQUEST)
    if activation.order.status != 'paid':
        return Response({'error': 'Zamówienie powiązane z tym kodem nie jest jeszcze opłacone.'},
                        status=status.HTTP_400_BAD_REQUEST)

    # --- Główna logika biznesowa w jednej, atomowej transakcji ---
    with transaction.atomic():
        order = activation.order
        company = order.company

        # Krok 1: Jeśli firma dla tego zamówienia nie istnieje, stwórz ją.
        if not company:
            company_name = f"Firma {order.email or request.user.email}"
            company = Company.objects.create(name=company_name)

            # Połącz nowo utworzoną firmę z zamówieniem na stałe.
            order.company = company
            order.save(update_fields=['company'])

        # Krok 2: Stwórz profil Technika.
        technician = Technician.objects.create(
            user=request.user,
            company=company,
            first_name=request.user.first_name or '',
            last_name=request.user.last_name or '',
            email=request.user.email or '',
            is_active=True,
            # Pierwszy użytkownik, który realizuje kod dla zamówienia, zostaje adminem.
            # `used_by` na order jest tu jeszcze None, więc warunek jest spełniony.
            role=Technician.ROLE_ADMIN
        )

        # Krok 3: Oznacz kod jako wykorzystany.
        # Zakładam, że metoda .redeem() robi `self.used = True`, `self.used_by = user` i `self.save()`
        activation.redeem(request.user)

    # Krok 4: Zwróć zaktualizowane dane użytkownika do frontendu.
    # Musimy ponownie pobrać obiekt użytkownika z bazy, aby zobaczyć `technician_profile`.
    request.user.refresh_from_db()
    user_data = UserProfileSerializer(instance=request.user, context={'request': request}).data

    return Response({
        'detail': 'Kod zrealizowany! Twoje konto jest teraz w pełni aktywne.',
        'user': user_data
    }, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsCompanyAdmin]) # Tylko admin może generować raporty
def export_device_pdf(request, device_id):
    """
    Generuje i zwraca raport PDF dla urządzenia o podanym ID.
    """
    try:
        # Pobieramy obiekt urządzenia, upewniając się, że należy do firmy użytkownika
        company = request.user.technician_profile.company
        device = FiscalDevice.objects.select_related('owner', 'brand').get(
            id=device_id,
            owner__company=company
        )
    except FiscalDevice.DoesNotExist:
        return Response({'error': 'Nie znaleziono urządzenia.'}, status=status.HTTP_404_NOT_FOUND)

    # Przygotowujemy kontekst dla szablonu HTML
    context = {
        'device': device,
        'generation_date': timezone.now().strftime('%Y-%m-%d %H:%M:%S')
    }

    # Renderujemy szablon HTML do stringa
    html_string = render_to_string('device_report.html', context)

    # Generujemy PDF za pomocą WeasyPrint
    pdf_file = HTML(string=html_string).write_pdf()

    # Tworzymy odpowiedź HTTP z plikiem PDF
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="raport_urzadzenia_{device.unique_number}.pdf"'

    return response

from django.db.models import Count
from django.db.models.functions import TruncMonth

class ChartView(APIView):
    """
    Widok dostarczający zagregowane dane do wykresów na pulpicie.
    Wszystkie dane są filtrowane w kontekście firmy zalogowanego użytkownika.
    """
    permission_classes = [permissions.IsAuthenticated, IsCompanyMember]

    def get(self, request, *args, **kwargs):
        company = request.user.technician_profile.company
        current_year = timezone.now().year

        # 1. Wykres: Zgłoszenia wg statusu (Pie Chart)
        tickets_by_status_qs = ServiceTicket.objects.filter(
            client__company=company
        ).values('status').annotate(count=Count('id')).order_by('status')

        # Mapowanie kluczy statusu na czytelne etykiety
        status_labels_map = dict(ServiceTicket.Status.choices)
        tickets_by_status_data = {
            "labels": [status_labels_map.get(item['status'], item['status']) for item in tickets_by_status_qs],
            "data": [item['count'] for item in tickets_by_status_qs]
        }

        # 2. Wykres: Zgłoszenia w czasie (Line Chart)
        # Przygotowujemy dane dla ostatnich 12 miesięcy
        today = timezone.now().date()
        twelve_months_ago = today - timedelta(days=365)

        # Zgłoszenia utworzone
        created_tickets_qs = ServiceTicket.objects.filter(
            client__company=company,
            created_at__gte=twelve_months_ago
        ).annotate(
            month=TruncMonth('created_at')
        ).values('month').annotate(count=Count('id')).order_by('month')

        # Zgłoszenia zamknięte
        closed_tickets_qs = ServiceTicket.objects.filter(
            client__company=company,
            completed_at__gte=twelve_months_ago
        ).annotate(
            month=TruncMonth('completed_at')
        ).values('month').annotate(count=Count('id')).order_by('month')

        # Przetwarzanie danych do formatu wykresu
        monthly_data = defaultdict(lambda: {'created': 0, 'closed': 0})
        for item in created_tickets_qs:
            monthly_data[item['month'].strftime('%Y-%m')]['created'] = item['count']
        for item in closed_tickets_qs:
            monthly_data[item['month'].strftime('%Y-%m')]['closed'] = item['count']

        # Sortowanie i formatowanie finalnego outputu
        sorted_months = sorted(monthly_data.keys())
        tickets_over_time_data = {
            "labels": [datetime.strptime(m, '%Y-%m').strftime('%B %Y') for m in sorted_months],
            "datasets": [
                {
                    "label": "Nowe zgłoszenia",
                    "data": [monthly_data[m]['created'] for m in sorted_months],
                    "backgroundColor": 'rgba(75, 192, 192, 0.5)',
                    "borderColor": 'rgb(75, 192, 192)',
                },
                {
                    "label": "Zamknięte zgłoszenia",
                    "data": [monthly_data[m]['closed'] for m in sorted_months],
                    "backgroundColor": 'rgba(255, 99, 132, 0.5)',
                    "borderColor": 'rgb(255, 99, 132)',
                }
            ]
        }

        # 3. Wykres: Urządzenia wg statusu (Doughnut Chart)
        devices_by_status_qs = FiscalDevice.objects.filter(
            owner__company=company
        ).values('status').annotate(count=Count('id')).order_by('status')

        device_status_map = dict(FiscalDevice.Status.choices)
        devices_by_status_data = {
            "labels": [device_status_map.get(item['status'], item['status']) for item in devices_by_status_qs],
            "data": [item['count'] for item in devices_by_status_qs]
        }

        # 4. Dane: Certyfikaty wygasające w ciągu 90 dni
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
            }
            for cert in expiring_certs_qs
        ]

        # Kompilacja wszystkich danych w jedną odpowiedź
        response_data = {
            "tickets_by_status": tickets_by_status_data,
            "tickets_over_time": tickets_over_time_data,
            "devices_by_status": devices_by_status_data,
            "expiring_certifications": expiring_certs_data,
        }

        return Response(response_data, status=status.HTTP_200_OK)