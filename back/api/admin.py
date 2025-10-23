from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (
    CustomUser,
    Client,
    Manufacturer,
    Technician,
    Certification,
    FiscalDevice,
    ServiceTicket
)

class TechnicianInline(admin.StackedInline):
    model = Technician
    can_delete = False
    verbose_name_plural = 'Profil serwisanta'


@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin):
    inlines = (TechnicianInline,)

@admin.register(Technician)
class TechnicianAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'phone_number')
    autocomplete_fields = ('user',)



class FiscalDeviceInline(admin.TabularInline):
    model = FiscalDevice
    extra = 0
    show_change_link = True
    fields = ('model_name', 'serial_number', 'brand', 'status')

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'nip', 'regon', 'email', 'phone_number')
    search_fields = ('name', 'nip', 'regon')
    inlines = [FiscalDeviceInline]

@admin.register(Manufacturer)
class ManufacturerAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(FiscalDevice)
class FiscalDeviceAdmin(admin.ModelAdmin):
    list_display = ('model_name', 'unique_number', 'serial_number', 'brand', 'owner', 'status', 'sale_date')
    list_filter = ('status', 'brand')
    search_fields = ('model_name', 'serial_number', 'unique_number', 'owner__name')
    autocomplete_fields = ('owner', 'brand')



@admin.register(Certification)
class CertificationAdmin(admin.ModelAdmin):
    list_display = ('technician', 'manufacturer', 'certificate_number', 'issue_date', 'expiry_date')
    list_filter = ('manufacturer',)
    search_fields = ('technician__user__username', 'certificate_number')
    autocomplete_fields = ('technician', 'manufacturer')

@admin.register(ServiceTicket)
class ServiceTicketAdmin(admin.ModelAdmin):
    list_display = ('ticket_number', 'title', 'client', 'device', 'assigned_technician', 'status', 'created_at')
    list_filter = ('status', 'ticket_type', 'assigned_technician')
    search_fields = ('ticket_number', 'title', 'client__name', 'device__serial_number')
    autocomplete_fields = ('client', 'device', 'assigned_technician')
    # Rozdzielenie pól na sekcje dla lepszej czytelności
    fieldsets = (
        ('Informacje o zgłoszeniu', {
            'fields': ('ticket_number', 'title', 'ticket_type', 'status', 'description')
        }),
        ('Powiązania', {
            'fields': ('client', 'device', 'assigned_technician')
        }),
        ('Rozwiązanie i daty', {
            'fields': ('resolution_notes', 'scheduled_for', 'completed_at')
        }),
    )
    readonly_fields = ('ticket_number', 'created_at')