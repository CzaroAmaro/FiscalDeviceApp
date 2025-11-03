from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings


class CustomUser(AbstractUser):
    """
    Rozszerzony model użytkownika.
    Pozostawiony pusty, aby w przyszłości łatwo go było rozbudować.
    """
    pass


class Company(models.Model):
    """Model przechowujący dane firmy serwisowej."""
    name = models.CharField(max_length=255, verbose_name="Nazwa firmy")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Technician(models.Model):
    """Profil serwisanta, rozszerzający model użytkownika."""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="technician_profile",
        verbose_name="Konto użytkownika",
        null=True,
        blank=True
    )
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='technicians')
    first_name = models.CharField(max_length=150, verbose_name="Imię")
    last_name = models.CharField(max_length=150, verbose_name="Nazwisko")
    email = models.EmailField(max_length=254, blank=True, verbose_name="Adres e-mail")
    phone_number = models.CharField(max_length=20, blank=True, verbose_name="Telefon służbowy")
    is_active = models.BooleanField(default=True, verbose_name="Aktywny")

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return self.full_name

    class Meta:
        verbose_name = "Serwisant"
        verbose_name_plural = "Serwisanci"
