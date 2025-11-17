from django.db import models
from .clients import Client
from .manufacturers import Manufacturer


class FiscalDevice(models.Model):
    """Fiscal device owned by a client (company via client.company)."""

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
