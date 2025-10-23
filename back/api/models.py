from datetime import date

from django.db import models
from django.contrib.auth.models import AbstractUser

from django.conf import settings


class CustomUser(AbstractUser):
    pass

class Client(models.Model):
    name = models.CharField(max_length=255, verbose_name="Nazwa firmy/Imię i nazwisko")
    address = models.CharField(max_length=255, verbose_name="Adres")
    nip = models.CharField(max_length=10, unique=True, verbose_name="NIP")
    phone_number = models.CharField(max_length=20, blank=True, verbose_name="Numer telefonu")
    email = models.EmailField(max_length=100, blank=True, verbose_name="Adres e-mail")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Data dodania")
    regon = models.CharField(max_length=14, blank=True, verbose_name="REGON")

    def __str__(self):
        return f"{self.name} (NIP: {self.nip})"

    class Meta:
        verbose_name = "Klient"
        verbose_name_plural = "Klienci"
        ordering = ['name']

class Manufacturer(models.Model):
    """Słownik producentów urządzeń (np. Novitus, Elzab)."""
    name = models.CharField(max_length=100, unique=True, verbose_name="Nazwa producenta")

    def __str__(self):
        return self.name

class FiscalDevice(models.Model):
    DEVICE_STATUS_CHOICES = [
        ('active', 'Aktywna'),
        ('inactive', 'Niewykorzystywana'),
        ('serviced', 'W serwisie'),
        ('decommissioned', 'Wycofana'),
    ]
    brand = models.ForeignKey(Manufacturer, on_delete=models.PROTECT, verbose_name="Marka/Producent", null=True)
    model_name = models.CharField(max_length=100, verbose_name="Model urządzenia")
    unique_number = models.CharField(max_length=100, unique=True, null=True, verbose_name="Numer unikatowy")
    serial_number = models.CharField(max_length=100, verbose_name="Numer seryjny")
    sale_date = models.DateField(verbose_name="Data sprzedaży")
    last_service_date = models.DateField(null=True, blank=True, verbose_name="Data ostatniego przeglądu")
    status = models.CharField(max_length=20, choices=DEVICE_STATUS_CHOICES, default='active', verbose_name="Status")
    operating_instructions = models.TextField(blank=True, verbose_name="Sposób użytkowania")
    remarks = models.TextField(blank=True, verbose_name="Uwagi")

    owner = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='devices', verbose_name="Właściciel")

    def __str__(self):
        return f"{self.model_name} - S/N: {self.serial_number}"

    class Meta:
        verbose_name = "Urządzenie fiskalne"
        verbose_name_plural = "Urządzenia fiskalne"
        ordering = ['-last_service_date']



class Technician(models.Model):
    """Profil serwisanta, rozszerzający model użytkownika."""
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="technician_profile")
    phone_number = models.CharField(max_length=20, blank=True, verbose_name="Telefon służbowy")
    is_active = models.BooleanField(default=True, verbose_name="Aktywny")

    def __str__(self):
        return self.user.get_full_name() or self.user.username

    class Meta:
        verbose_name = "Serwisant"
        verbose_name_plural = "Serwisanci"

class Certification(models.Model):
    """Reprezentuje certyfikat/legitymację serwisową danego technika od konkretnego producenta."""
    technician = models.ForeignKey(Technician, on_delete=models.CASCADE, related_name="certifications")
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.CASCADE, related_name="certified_technicians")
    certificate_number = models.CharField(max_length=100, verbose_name="Numer legitymacji/certyfikatu")
    issue_date = models.DateField(verbose_name="Data wydania")
    expiry_date = models.DateField(verbose_name="Data ważności")

    class Meta:
        # Gwarantuje, że jeden serwisant nie może mieć dwóch takich samych certyfikatów od tego samego producenta
        unique_together = ('technician', 'manufacturer', 'certificate_number')

    def __str__(self):
        return f"Certyfikat {self.manufacturer.name} dla {self.technician}"


class ServiceTicket(models.Model):
    """Główny model reprezentujący zlecenie serwisowe."""
    TICKET_STATUS_CHOICES = [('open', 'Otwarte'), ('in_progress', 'W toku'), ('closed', 'Zamknięte')]
    TICKET_TYPE_CHOICES = [('service', 'Przegląd'), ('reading', 'Odczyt'), ('repair', 'Naprawa'), ('other', 'Inne')]

    ticket_number = models.CharField(max_length=50, unique=True, blank=True, verbose_name="Numer zgłoszenia")
    title = models.CharField(max_length=255, verbose_name="Tytuł zgłoszenia")
    description = models.TextField(verbose_name="Opis zgłoszenia")
    ticket_type = models.CharField(max_length=20, choices=TICKET_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=TICKET_STATUS_CHOICES, default='open')
    scheduled_for = models.DateTimeField(null=True, blank=True, verbose_name="Zaplanowano na")
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="Data ukończenia")

    client = models.ForeignKey(Client, on_delete=models.PROTECT, related_name="tickets")
    device = models.ForeignKey(FiscalDevice, on_delete=models.PROTECT, related_name="tickets")
    assigned_technician = models.ForeignKey(Technician, on_delete=models.SET_NULL, null=True, blank=True,
                                            related_name="tickets")

    created_at = models.DateTimeField(auto_now_add=True)
    resolution_notes = models.TextField(blank=True, verbose_name="Notatki z wykonania / Rozwiązanie")

    # Metoda do auto-generowania numeru, jak w poprzedniej propozycji
    def save(self, *args, **kwargs):
        if not self.ticket_number:
            last_ticket = ServiceTicket.objects.order_by('id').last()
            new_id = (last_ticket.id if last_ticket else 0) + 1
            self.ticket_number = f"ZGL-{date.today().year}-{new_id:04d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.ticket_number}: {self.title}"