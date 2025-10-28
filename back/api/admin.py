# admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (
    CustomUser, Client, Manufacturer, Technician, Certification, FiscalDevice, ServiceTicket
)


# --- Konfiguracja Użytkowników i Serwisantów ---

class TechnicianInline(admin.StackedInline):
    model = Technician
    can_delete = False
    verbose_name_plural = 'Profil serwisanta'
    fields = ('phone_number', 'is_active')

@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin):
    inlines = (TechnicianInline,)

@admin.register(Technician)
class TechnicianAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'phone_number', 'is_active')
    list_filter = ('is_active',)
    # Poniższe pola są poprawne. Ostrzeżenie z IDE to fałszywy alarm.
    # Django poprawnie przeszukuje relację `user`.
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'phone_number')
    raw_id_fields = ('user',)


# --- Konfiguracja Klientów, Producentów i Urządzeń ---

class FiscalDeviceInline(admin.TabularInline):
    model = FiscalDevice
    extra = 0
    show_change_link = True
    fields = ('model_name', 'serial_number', 'status')
    readonly_fields = ('model_name', 'serial_number', 'status')
    raw_id_fields = ('brand',)

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'nip', 'regon', 'phone_number', 'email')
    search_fields = ('name', 'nip', 'regon')
    inlines = [FiscalDeviceInline]

@admin.register(Manufacturer)
class ManufacturerAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(FiscalDevice)
class FiscalDeviceAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'owner', 'status', 'sale_date', 'last_service_date')
    list_filter = ('status', 'brand')
    search_fields = ('model_name', 'serial_number', 'unique_number', 'owner__name')
    autocomplete_fields = ('owner', 'brand')
    date_hierarchy = 'sale_date'


# --- Konfiguracja Certyfikatów i Zgłoszeń Serwisowych ---

@admin.register(Certification)
class CertificationAdmin(admin.ModelAdmin):
    list_display = ('technician', 'manufacturer', 'certificate_number', 'issue_date', 'expiry_date')
    list_filter = ('manufacturer',)
    # Poniższe pole jest poprawne. Ostrzeżenie z IDE to fałszywy alarm.
    # Django poprawnie przeszukuje zagnieżdżoną relację `technician__user`.
    search_fields = ('technician__user__username', 'certificate_number')
    autocomplete_fields = ('technician', 'manufacturer')

@admin.register(ServiceTicket)
class ServiceTicketAdmin(admin.ModelAdmin):
    list_display = ('ticket_number', 'title', 'client', 'status', 'assigned_technician', 'created_at')
    list_filter = ('status', 'ticket_type', 'assigned_technician')
    search_fields = ('ticket_number', 'title', 'client__name', 'device__serial_number')
    autocomplete_fields = ('client', 'device', 'assigned_technician')
    readonly_fields = ('ticket_number', 'created_at', 'completed_at')
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Informacje o zgłoszeniu', {
            'fields': ('ticket_number', 'title', 'ticket_type', 'status', 'description')
        }),
        ('Powiązania', {
            'fields': ('client', 'device', 'assigned_technician')
        }),
        ('Rozwiązanie i daty', {
            'fields': ('resolution_notes', 'scheduled_for', 'created_at', 'completed_at')
        }),
    )