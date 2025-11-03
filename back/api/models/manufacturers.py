from django.db import models
from .users import Technician, Company


class Manufacturer(models.Model):
    """Słownik producentów urządzeń."""
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='manufacturers')
    name = models.CharField(max_length=100, unique=True, verbose_name="Nazwa producenta")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Producent"
        verbose_name_plural = "Producenci"
        ordering = ['name']


class Certification(models.Model):
    """Certyfikat serwisowy technika dla danego producenta."""
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='certifications')
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
        constraints = [
            models.UniqueConstraint(
                fields=['technician', 'manufacturer'],
                name='unique_technician_manufacturer_certification'
            )
        ]
