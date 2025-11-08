from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models.users import CustomUser, Company, Technician
from .models.clients import Client
from .models.manufacturers import Manufacturer, Certification
from .models.devices import FiscalDevice
from .models.tickets import ServiceTicket
from .models.billing import Order, ActivationCode

# --- Konfiguracja Użytkowników, Firm i Serwisantów ---

class TechnicianInline(admin.StackedInline):
    model = Technician
    can_delete = False
    verbose_name_plural = 'Profil serwisanta'
    fields = ('company', 'phone_number', 'is_active', 'is_company_admin')
    autocomplete_fields = ['company']

@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin):
    """Rozszerzony panel użytkownika z profilem serwisanta."""
    inlines = (TechnicianInline,)

# DODAJEMY REJESTRACJĘ MODELU COMPANY
@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    """Panel administracyjny dla modelu Company."""
    list_display = ('name', 'created_at')
    search_fields = ('name',)

@admin.register(Technician)
class TechnicianAdmin(admin.ModelAdmin):
    """Panel dla bezpośredniej edycji serwisantów."""
    list_display = ('full_name', 'email', 'company', 'role', 'is_active', 'has_user_account')
    list_filter = ('company', 'role', 'is_active')
    search_fields = ('first_name', 'last_name', 'email', 'user__username')
    fieldsets = (
        ('Dane Osobowe (Profil Serwisanta)', {
            'fields': ('first_name', 'last_name', 'email', 'phone_number')
        }),
        ('Przynależność i Rola', {
            'fields': ('company', 'role', 'is_active')
        }),
        ('Konto w Aplikacji (opcjonalne)', {
            'fields': ('user',)
        }),
    )

    autocomplete_fields = ('user',)

    # Metoda do wyświetlania statusu konta użytkownika w liście
    @admin.display(description='Posiada konto', boolean=True)
    def has_user_account(self, obj):
        return obj.user is not None


# --- Konfiguracja Klientów, Producentów i Urządzeń ---

class FiscalDeviceInline(admin.TabularInline):
    model = FiscalDevice
    extra = 0
    show_change_link = True
    fields = ('model_name', 'serial_number', 'status', 'sale_date')
    readonly_fields = fields # Wszystkie pola tylko do odczytu
    classes = ('collapse',) # Ukrywa domyślnie sekcję

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'nip', 'company', 'email')
    search_fields = ('name', 'nip', 'regon')
    list_filter = ('company',)
    inlines = [FiscalDeviceInline]
    autocomplete_fields = ['company']

@admin.register(Manufacturer)
class ManufacturerAdmin(admin.ModelAdmin):
    list_display = ('name', 'company')
    search_fields = ('name',)
    list_filter = ('company',)
    autocomplete_fields = ['company']

@admin.register(FiscalDevice)
class FiscalDeviceAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'owner', 'status', 'sale_date', 'last_service_date')
    list_filter = ('status', 'brand', 'owner__company')
    search_fields = ('model_name', 'serial_number', 'unique_number', 'owner__name')
    autocomplete_fields = ('owner', 'brand')
    date_hierarchy = 'sale_date'

# --- Konfiguracja Certyfikatów i Zgłoszeń Serwisowych ---

@admin.register(Certification)
class CertificationAdmin(admin.ModelAdmin):
    list_display = ('technician', 'manufacturer', 'certificate_number', 'issue_date', 'expiry_date')
    list_filter = ('manufacturer__company', 'manufacturer')
    search_fields = ('technician__full_name', 'certificate_number', 'manufacturer__name')
    autocomplete_fields = ('technician', 'manufacturer')
    date_hierarchy = 'issue_date'

@admin.register(ServiceTicket)
class ServiceTicketAdmin(admin.ModelAdmin):
    list_display = ('ticket_number', 'title', 'client', 'status', 'assigned_technician', 'created_at')
    list_filter = ('status', 'ticket_type', 'client__company')
    search_fields = ('ticket_number', 'title', 'client__name', 'device__serial_number')
    autocomplete_fields = ('client', 'device', 'assigned_technician')
    readonly_fields = ('ticket_number', 'created_at', 'completed_at')
    date_hierarchy = 'created_at'

    # Twoje fieldsets są świetne, zostawiamy je
    fieldsets = (
        ('Informacje o zgłoszeniu', {
            'fields': ('ticket_number', 'title', 'ticket_type', 'status', 'description')
        }),
        ('Powiązania', {
            'fields': ('client', 'device', 'assigned_technician')
        }),
        ('Rozwiązanie i daty', {
            'fields': ('resolution_notes', 'scheduled_for', 'created_at', 'completed_at'),
            'classes': ('collapse',) # Ukrywa sekcję domyślnie
        }),
    )

# --- DODAJEMY REJESTRACJĘ MODELI BILLING ---

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'company', 'status', 'amount_cents', 'currency', 'created_at')
    list_filter = ('status', 'currency', 'company')
    search_fields = ('id', 'stripe_session_id', 'company__name', 'email')
    date_hierarchy = 'created_at'
    autocomplete_fields = ['company']

@admin.register(ActivationCode)
class ActivationCodeAdmin(admin.ModelAdmin):
    list_display = ('code', 'order_company', 'used', 'used_by', 'expires_at')
    list_filter = ('used', 'order__company')
    search_fields = ('code', 'email', 'used_by__username', 'order__company__name')
    autocomplete_fields = ['order', 'used_by']

    @admin.display(description='Company', ordering='order__company')
    def order_company(self, obj):
        if obj.order and obj.order.company:
            return obj.order.company.name
        return "N/A"