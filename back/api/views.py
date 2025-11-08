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
    ActivationCodeReadSerializer, ActivationCodeWriteSerializer, CompanySerializer, UserProfileSerializer
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
            return user.technician_profile.is_company_admin
        return False

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
            CustomUserSerializer(user, context=self.get_serializer_context()).data,
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
        read_serializer = ManufacturerSummarySerializer(instance, context=self.get_serializer_context())

        headers = self.get_success_headers(write_serializer.data)
        return Response(read_serializer.data, status=status.HTTP_201_CREATED, headers=headers)


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
    Opcjonalne: frontend może wysłać session_id po przekierowaniu z Stripe.
    Funkcja spróbuje pobrać session, upewnić się, że payment_status == 'paid' i
    zwrócić ActivationCode (jeśli został wygenerowany). Webhook jest głównym źródłem prawdy,
    ale endpoint ten pozwala od razu zwrócić kod użytkownikowi natychmiast po przekierowaniu.
    """
    session_id = request.data.get('session_id')
    if not session_id:
        return Response({'error': 'Brak session_id'}, status=status.HTTP_400_BAD_REQUEST)

    stripe.api_key = settings.STRIPE_SECRET_KEY
    try:
        session = stripe.checkout.Session.retrieve(session_id)
        if session.get('payment_status') != 'paid':
            return Response({'error': 'Payment not paid yet'}, status=status.HTTP_400_BAD_REQUEST)

        # Najpierw spróbuj znaleźć order po metadata.order_id
        metadata = session.get('metadata') or {}
        order = None
        order_id = metadata.get('order_id')
        if order_id:
            try:
                order = Order.objects.get(id=order_id)
            except Order.DoesNotExist:
                order = None
        if not order:
            order = Order.objects.filter(stripe_session_id=session_id).first()

        # jeśli order nie istnieje, stworzymy go defensywnie
        if not order:
            company = Company.objects.create(name=f"Company - {session.customer_details.email or session_id}")
            order = Order.objects.create(
                company=company,
                email=session.customer_details.email or '',
                stripe_session_id=session_id,
                stripe_payment_intent=session.get('payment_intent'),
                status='paid',
                amount_cents=session.get('amount_total') or 0,
                currency=(session.get('currency') or 'pln').upper()
            )
        else:
            # uaktualnij order status na paid jeśli trzeba
            if order.status != 'paid':
                order.status = 'paid'
                order.stripe_payment_intent = session.get('payment_intent')
                order.amount_cents = order.amount_cents or session.get('amount_total') or 0
                order.currency = (session.get('currency') or order.currency or 'pln').upper()
                order.save()

        # Stwórz activation code jeśli jeszcze nie istnieje
        activation = ActivationCode.objects.filter(order=order).first()
        if not activation:
            activation = ActivationCode.create_for_order(order, email=order.email)

        return Response({'code': activation.code}, status=status.HTTP_200_OK)

    except stripe.error.InvalidRequestError as e:
        return Response({'error': 'Stripe error: ' + str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def stripe_webhook(request):
    """
    Webhook handler (pamiętaj: zarejestruj STRIPE_WEBHOOK_SECRET w settings i Stripe Dashboard).
    Obsługujemy checkout.session.completed -> aktualizujemy lub tworzymy Order + ActivationCode.
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
        session_id = session.get('id')
        metadata = session.get('metadata') or {}
        order_id = metadata.get('order_id')

        # idempotentnie: jeżeli order z tym stripe_session_id już oznaczony jako paid -> ok
        existing_paid = Order.objects.filter(stripe_session_id=session_id, status='paid').exists()
        if existing_paid:
            return Response({'status': 'already_processed'}, status=status.HTTP_200_OK)

        try:
            with transaction.atomic():
                order = None
                if order_id:
                    order = Order.objects.filter(id=order_id).first()

                if not order:
                    order = Order.objects.filter(stripe_session_id=session_id).first()

                if not order:
                    # defensywnie - stwórz nowe zamówienie przypisane do nowej firmy tymczasowej
                    company = Company.objects.create(name=f"Company - {session.get('customer_details', {}).get('email', session_id)}")
                    order = Order.objects.create(
                        company=company,
                        email=session.get('customer_details', {}).get('email', '') or '',
                        stripe_session_id=session_id,
                        stripe_payment_intent=session.get('payment_intent'),
                        status='paid',
                        amount_cents=session.get('amount_total') or 0,
                        currency=(session.get('currency') or 'pln').upper()
                    )
                else:
                    # Aktualizuj istniejący order do paid
                    order.status = 'paid'
                    order.stripe_payment_intent = session.get('payment_intent')
                    order.amount_cents = order.amount_cents or session.get('amount_total') or 0
                    order.currency = (session.get('currency') or order.currency or 'pln').upper()
                    # Jeżeli order miał None company, spróbuj ustawić tymczasową firmę
                    if not order.company:
                        company = Company.objects.create(name=f"Company - {session.get('customer_details', {}).get('email', session_id)}")
                        order.company = company
                    order.save()

                # Utwórz ActivationCode tylko raz
                if not ActivationCode.objects.filter(order=order).exists():
                    ActivationCode.create_for_order(order, email=order.email)
        except Exception as e:
            # Nie przerywamy webhooka — ale loguj błąd
            # (tu możesz dodać logging / alert)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
    Umożliwia zalogowanemu użytkownikowi zrealizować kod aktywacyjny i utworzyć profil Technician
    powiązany z order.company. Wymagany body: { "code": "XXXX" }
    """
    code_value = request.data.get('code')
    if not code_value:
        return Response({'error': 'Brak kodu'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        activation = ActivationCode.objects.select_related('order__company').get(code=code_value)
    except ActivationCode.DoesNotExist:
        return Response({'error': 'Nieprawidłowy kod'}, status=status.HTTP_404_NOT_FOUND)

    # Sprawdzenia
    if activation.used:
        return Response({'error': 'Kod został już użyty'}, status=status.HTTP_400_BAD_REQUEST)

    # Dodatkowe sprawdzenie: kod przypisany do emaila kupującego (opcjonalne)
    if activation.email and activation.email != request.user.email:
        return Response({'error': 'Kod przypisany do innego adresu e-mail'}, status=status.HTTP_403_FORBIDDEN)

    # Jeżeli użytkownik już ma profil Technician — odrzuć (możesz też zezwolić na powiązanie)
    if hasattr(request.user, 'technician_profile'):
        return Response({'error': 'Twoje konto jest już powiązane z profilem serwisanta.'}, status=status.HTTP_400_BAD_REQUEST)

    # Stwórz Technician powiązany z activation.order.company
    company = activation.order.company
    if not company:
        return Response({'error': 'Kod nie jest powiązany z żadną firmą.'}, status=status.HTTP_400_BAD_REQUEST)

    with transaction.atomic():
        tech = Technician.objects.create(
            user=request.user,
            company=company,
            first_name=request.user.first_name or '',
            last_name=request.user.last_name or '',
            email=request.user.email or '',
            is_active=True,
            is_company_admin=False
        )
        activation.redeem(request.user)

    request.user.refresh_from_db()
    user_data = UserProfileSerializer(request.user, context={'request': request}).data
    return Response({
        'detail': 'Kod zrealizowany, profil serwisanta utworzony.',
        'user': user_data
    }, status=status.HTTP_200_OK)