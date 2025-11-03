from django.db import models


class Client(models.Model):
    """Model przechowujący dane klienta (firma lub osoba)."""
    name = models.CharField(max_length=255, verbose_name="Nazwa firmy/Imię i nazwisko")
    address = models.CharField(max_length=255, verbose_name="Adres")
    nip = models.CharField(max_length=10, unique=True, verbose_name="NIP")
    regon = models.CharField(max_length=14, blank=True, verbose_name="REGON")
    phone_number = models.CharField(max_length=20, blank=True, verbose_name="Numer telefonu")
    email = models.EmailField(max_length=100, blank=True, verbose_name="Adres e-mail")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Data dodania")

    def __str__(self):
        return f"{self.name} (NIP: {self.nip})"

    class Meta:
        verbose_name = "Klient"
        verbose_name_plural = "Klienci"
        ordering = ['name']
