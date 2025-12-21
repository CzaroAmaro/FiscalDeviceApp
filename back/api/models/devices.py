from django.db import models
from .clients import Client
from .manufacturers import Manufacturer
from django.conf import settings


class FiscalDevice(models.Model):

    class Status(models.TextChoices):
        ACTIVE = 'active', 'Aktywna'
        INACTIVE = 'inactive', 'Niewykorzystywana'
        SERVICED = 'serviced', 'W serwisie'
        DECOMMISSIONED = 'decommissioned', 'Wycofana'

    brand = models.ForeignKey(Manufacturer, on_delete=models.PROTECT, verbose_name="Marka/Producent")
    model_name = models.CharField(max_length=100, verbose_name="Model urządzenia")
    unique_number = models.CharField(max_length=100, unique=True, db_index=True, verbose_name="Numer unikatowy")
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
        indexes = [
            models.Index(fields=['owner']),
            models.Index(fields=['serial_number']),
        ]


class DeviceHistoryEntry(models.Model):

    class ActionType(models.TextChoices):
        DEVICE_CREATED = 'DEVICE_CREATED', 'Utworzono urządzenie'
        SERVICE_PERFORMED = 'SERVICE_PERFORMED', 'Wykonano przegląd'
        TICKET_COMPLETED = 'TICKET_COMPLETED', 'Zakończono zlecenie'
        TICKET_CREATED = 'TICKET_CREATED', 'Utworzono zlecenie'
        STATUS_CHANGED = 'STATUS_CHANGED', 'Zmieniono status'

    device = models.ForeignKey(
        'FiscalDevice',
        on_delete=models.CASCADE,
        related_name='history_entries',
        verbose_name="Urządzenie"
    )

    event_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data zdarzenia"
    )

    action_type = models.CharField(
        max_length=50,
        choices=ActionType.choices,
        verbose_name="Rodzaj akcji"
    )

    description = models.TextField(
        verbose_name="Opis zdarzenia"
    )

    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Wykonane przez"
    )

    class Meta:
        verbose_name = "Wpis historii urządzenia"
        verbose_name_plural = "Wpisy historii urządzeń"
        ordering = ['-event_date']  # Najnowsze wpisy na górze

    def __str__(self):
        return f"[{self.event_date.strftime('%Y-%m-%d %H:%M')}] {self.device}: {self.get_action_type_display()}"