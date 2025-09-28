from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    pass

class Client(models.Model):
    name = models.CharField(max_length=200, verbose_name="Nazwa firmy/Imię i nazwisko")
    address = models.CharField(max_length=255, verbose_name="Adres")
    nip = models.CharField(max_length=10, unique=True, verbose_name="NIP")
    phone_number = models.CharField(max_length=20, blank=True, verbose_name="Numer telefonu")
    email = models.EmailField(max_length=100, blank=True, verbose_name="Adres e-mail")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Data dodania")

    def __str__(self):
        return f"{self.name} (NIP: {self.nip})"

    class Meta:
        verbose_name = "Klient"
        verbose_name_plural = "Klienci"
        ordering = ['name']

class FiscalDevice(models.Model):
    DEVICE_STATUS_CHOICES = [
        ('active', 'Aktywna'),
        ('inactive', 'Niewykorzystywana'),
        ('serviced', 'W serwisie'),
        ('decommissioned', 'Wycofana'),
    ]

    model_name = models.CharField(max_length=100, verbose_name="Model urządzenia")
    serial_number = models.CharField(max_length=100, unique=True, verbose_name="Numer seryjny")
    production_date = models.DateField(verbose_name="Data produkcji")
    last_service_date = models.DateField(null=True, blank=True, verbose_name="Data ostatniego przeglądu")
    status = models.CharField(max_length=20, choices=DEVICE_STATUS_CHOICES, default='active', verbose_name="Status")

    owner = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='devices', verbose_name="Właściciel")

    def __str__(self):
        return f"{self.model_name} - S/N: {self.serial_number}"

    class Meta:
        verbose_name = "Urządzenie fiskalne"
        verbose_name_plural = "Urządzenia fiskalne"
        ordering = ['-last_service_date']

class ServiceRecord(models.Model):
    description = models.TextField(verbose_name="Opis czynności serwisowych")
    service_date = models.DateTimeField(auto_now_add=True, verbose_name="Data serwisu")

    device = models.ForeignKey(FiscalDevice, on_delete=models.CASCADE, related_name='service_history',
                               verbose_name="Urządzenie")
    technician = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True,
                                   verbose_name="Serwisant")

    def __str__(self):
        return f"Serwis dla {self.device.serial_number} w dniu {self.service_date.strftime('%Y-%m-%d')}"

    class Meta:
        verbose_name = "Wpis serwisowy"
        verbose_name_plural = "Wpisy serwisowe"
        ordering = ['-service_date']