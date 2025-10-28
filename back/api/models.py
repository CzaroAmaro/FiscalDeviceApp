# models.py
from datetime import date

from django.db import models, transaction
from django.contrib.auth.models import AbstractUser
from django.conf import settings

# --- Modele Użytkowników i Profilów ---

class CustomUser(AbstractUser):
    """
    Niestandardowy model użytkownika. Na razie pusty, ale stanowi dobrą praktykę
    na przyszłość, aby łatwo go rozszerzać bez migracji głównego modelu User.
    """
    pass

class Technician(models.Model):
    """Profil serwisanta, rozszerzający model użytkownika."""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="technician_profile",
        verbose_name="Użytkownik"
    )
    phone_number = models.CharField(max_length=20, blank=True, verbose_name="Telefon służbowy")
    is_active = models.BooleanField(default=True, verbose_name="Aktywny")

    def __str__(self):
        # Lepsze fallback, jeśli imię i nazwisko nie są ustawione
        return self.user.get_full_name() or self.user.username

    class Meta:
        verbose_name = "Serwisant"
        verbose_name_plural = "Serwisanci"

# --- Modele Słownikowe i Główne ---

class Client(models.Model):
    name = models.CharField(max_length=255, verbose_name="Nazwa firmy/Imię i nazwisko")
    address = models.CharField(max_length=255, verbose_name="Adres")
    nip = models.CharField(max_length=10, unique=True, verbose_name="NIP") # unique=True automatycznie tworzy indeks
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

    class Meta:
        verbose_name = "Producent"
        verbose_name_plural = "Producenci"
        ordering = ['name']

class Certification(models.Model):
    """Certyfikat serwisowy technika dla danego producenta."""
    technician = models.ForeignKey(Technician, on_delete=models.CASCADE, related_name="certifications")
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.CASCADE, related_name="certified_technicians")
    certificate_number = models.CharField(max_length=100, verbose_name="Numer legitymacji/certyfikatu")
    issue_date = models.DateField(verbose_name="Data wydania")
    expiry_date = models.DateField(verbose_name="Data ważności")

    def __str__(self):
        return f"Certyfikat {self.manufacturer.name} dla {self.technician}"

    class Meta:
        verbose_name = "Certyfikat"
        verbose_name_plural = "Certyfikaty"
        # Użycie constraints jest nowocześniejszym podejściem niż unique_together
        constraints = [
            models.UniqueConstraint(fields=['technician', 'manufacturer'], name='unique_technician_manufacturer_certification')
        ]


class FiscalDevice(models.Model):
    class Status(models.TextChoices):
        ACTIVE = 'active', 'Aktywna'
        INACTIVE = 'inactive', 'Niewykorzystywana'
        SERVICED = 'serviced', 'W serwisie'
        DECOMMISSIONED = 'decommissioned', 'Wycofana'

    brand = models.ForeignKey(Manufacturer, on_delete=models.PROTECT, verbose_name="Marka/Producent") # Usunięto null=True, marka powinna być wymagana
    model_name = models.CharField(max_length=100, verbose_name="Model urządzenia")
    # Indeks na numerze unikatowym poprawi wydajność wyszukiwania
    unique_number = models.CharField(max_length=100, unique=True, db_index=True, verbose_name="Numer unikatowy") # Usunięto null=True, powinien być wymagany
    serial_number = models.CharField(max_length=100, verbose_name="Numer seryjny")
    sale_date = models.DateField(verbose_name="Data sprzedaży")
    last_service_date = models.DateField(null=True, blank=True, verbose_name="Data ostatniego przeglądu")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE, verbose_name="Status")
    operating_instructions = models.TextField(blank=True, verbose_name="Sposób użytkowania")
    remarks = models.TextField(blank=True, verbose_name="Uwagi")
    owner = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='devices', verbose_name="Właściciel")

    def __str__(self):
        return f"{self.brand.name} {self.model_name} (SN: {self.serial_number})"

    class Meta:
        verbose_name = "Urządzenie fiskalne"
        verbose_name_plural = "Urządzenia fiskalne"
        ordering = ['-sale_date']


class ServiceTicket(models.Model):
    class Status(models.TextChoices):
        OPEN = 'open', 'Otwarte'
        IN_PROGRESS = 'in_progress', 'W toku'
        CLOSED = 'closed', 'Zamknięte'

    class TicketType(models.TextChoices):
        SERVICE = 'service', 'Przegląd'
        READING = 'reading', 'Odczyt'
        REPAIR = 'repair', 'Naprawa'
        OTHER = 'other', 'Inne'

    # db_index=True jest kluczowe dla wydajności wyszukiwania po numerze zgłoszenia
    ticket_number = models.CharField(max_length=50, unique=True, blank=True, db_index=True, verbose_name="Numer zgłoszenia")
    title = models.CharField(max_length=255, verbose_name="Tytuł zgłoszenia")
    description = models.TextField(verbose_name="Opis zgłoszenia")
    ticket_type = models.CharField(max_length=20, choices=TicketType.choices)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN, db_index=True)
    scheduled_for = models.DateTimeField(null=True, blank=True, verbose_name="Zaplanowano na")
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="Data ukończenia")

    client = models.ForeignKey(Client, on_delete=models.PROTECT, related_name="tickets", verbose_name="Klient")
    device = models.ForeignKey(FiscalDevice, on_delete=models.PROTECT, related_name="tickets", verbose_name="Urządzenie")
    assigned_technician = models.ForeignKey(
        Technician, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="assigned_tickets", verbose_name="Przypisany serwisant" # Zmieniona nazwa related_name na bardziej jednoznaczną
    )

    created_at = models.DateTimeField(auto_now_add=True)
    resolution_notes = models.TextField(blank=True, verbose_name="Notatki z wykonania / Rozwiązanie")

    def save(self, *args, **kwargs):
        # Generowanie numeru zgłoszenia tylko przy tworzeniu nowego obiektu
        if not self.pk and not self.ticket_number:
            self.ticket_number = self._generate_ticket_number()
        super().save(*args, **kwargs)

    @staticmethod
    def _generate_ticket_number():
        """
        Generuje nowy, unikalny numer zgłoszenia w sposób odporny na race conditions.
        Używa transakcji i `select_for_update` do zablokowania wiersza.
        """
        with transaction.atomic():
            # Blokujemy tabelę (lub ostatni wiersz) na czas odczytu, aby uniknąć race condition
            last_ticket = ServiceTicket.objects.select_for_update().order_by('id').last()
            last_id = last_ticket.id if last_ticket else 0
            new_id = last_id + 1
            # Format: ZGL-ROK-0001
            return f"ZGL-{date.today().year}-{new_id:04d}"

    def __str__(self):
        return f"{self.ticket_number}: {self.title}"

    class Meta:
        verbose_name = "Zgłoszenie serwisowe"
        verbose_name_plural = "Zgłoszenia serwisowe"
        ordering = ['-created_at']