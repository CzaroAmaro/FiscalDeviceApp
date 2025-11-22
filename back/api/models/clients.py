from django.db import models
from django.core.exceptions import ValidationError
from stdnum.pl import nip as std_nip


def validate_nip(value):
    if value:
        try:
            std_nip.validate(value)
        except Exception:
            raise ValidationError("Niepoprawny numer NIP.")


class Client(models.Model):
    """Client (customer) of the service provider company."""
    company = models.ForeignKey('Company', on_delete=models.CASCADE, related_name='clients')
    name = models.CharField(max_length=255, verbose_name="Nazwa firmy/Imię i nazwisko")
    address = models.CharField(max_length=255, verbose_name="Adres")
    nip = models.CharField(max_length=10, verbose_name="NIP", validators=[validate_nip])
    regon = models.CharField(max_length=14, blank=True, verbose_name="REGON")
    phone_number = models.CharField(max_length=20, blank=True, verbose_name="Numer telefonu")
    email = models.EmailField(max_length=100, blank=True, verbose_name="Adres e-mail")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Data dodania")
    latitude = models.FloatField(null=True, blank=True, verbose_name="Szerokość geograficzna")
    longitude = models.FloatField(null=True, blank=True, verbose_name="Długość geograficzna")

    def __str__(self):
        return f"{self.name} (NIP: {self.nip})"

    class Meta:
        verbose_name = "Klient"
        verbose_name_plural = "Klienci"
        ordering = ['name']
        constraints = [
            models.UniqueConstraint(fields=['company', 'nip'], name='unique_company_client_nip')
        ]
        indexes = [
            models.Index(fields=['company', 'nip']),
            models.Index(fields=['company', 'name']),
        ]
