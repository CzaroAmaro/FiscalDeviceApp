from datetime import date
from django.db import models, transaction
from .clients import Client
from .devices import FiscalDevice
from .users import Technician


class ServiceTicket(models.Model):
    """Zgłoszenie serwisowe powiązane z urządzeniem fiskalnym."""

    class Status(models.TextChoices):
        OPEN = 'open', 'Otwarte'
        IN_PROGRESS = 'in_progress', 'W toku'
        CLOSED = 'closed', 'Zamknięte'

    class TicketType(models.TextChoices):
        SERVICE = 'service', 'Przegląd'
        READING = 'reading', 'Odczyt'
        REPAIR = 'repair', 'Naprawa'
        OTHER = 'other', 'Inne'

    company = models.ForeignKey('users.Company', on_delete=models.CASCADE, related_name='tickets')
    ticket_number = models.CharField(max_length=50, unique=True, blank=True, db_index=True, verbose_name="Numer zgłoszenia")
    title = models.CharField(max_length=255, verbose_name="Tytuł zgłoszenia")
    description = models.TextField(verbose_name="Opis zgłoszenia")
    ticket_type = models.CharField(max_length=20, choices=TicketType.choices, verbose_name="Typ zgłoszenia")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN, db_index=True, verbose_name="Status")
    scheduled_for = models.DateTimeField(null=True, blank=True, verbose_name="Zaplanowano na")
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="Data ukończenia")

    client = models.ForeignKey(Client, on_delete=models.PROTECT, related_name="tickets", verbose_name="Klient")
    device = models.ForeignKey(FiscalDevice, on_delete=models.PROTECT, related_name="tickets", verbose_name="Urządzenie")
    assigned_technician = models.ForeignKey(
        Technician, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="assigned_tickets", verbose_name="Przypisany serwisant"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    resolution_notes = models.TextField(blank=True, verbose_name="Notatki z wykonania / Rozwiązanie")

    def save(self, *args, **kwargs):
        if not self.pk and not self.ticket_number:
            self.ticket_number = self._generate_ticket_number()
        super().save(*args, **kwargs)

    @staticmethod
    def _generate_ticket_number():
        """Generuje unikalny numer zgłoszenia w formacie ZGL-YYYY-0001."""
        with transaction.atomic():
            last_ticket = ServiceTicket.objects.select_for_update().order_by('id').last()
            last_id = last_ticket.id if last_ticket else 0
            new_id = last_id + 1
            return f"ZGL-{date.today().year}-{new_id:04d}"

    def __str__(self):
        return f"{self.ticket_number}: {self.title}"

    class Meta:
        verbose_name = "Zgłoszenie serwisowe"
        verbose_name_plural = "Zgłoszenia serwisowe"
        ordering = ['-created_at']
