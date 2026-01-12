from django.db import models
from .users import Company, Technician


class Manufacturer(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='manufacturers')
    name = models.CharField(max_length=100, verbose_name="Nazwa producenta")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Producent"
        verbose_name_plural = "Producenci"
        ordering = ['name']
        constraints = [
            models.UniqueConstraint(fields=['company', 'name'], name='unique_company_manufacturer')
        ]
        indexes = [
            models.Index(fields=['company', 'name']),
        ]


class Certification(models.Model):
    technician = models.ForeignKey(Technician, on_delete=models.CASCADE, related_name="certifications")
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.CASCADE, related_name="certifications")
    certificate_number = models.CharField(max_length=100, verbose_name="Numer legitymacji/certyfikatu")
    issue_date = models.DateField(verbose_name="Data wydania")
    expiry_date = models.DateField(verbose_name="Data ważności")

    def __str__(self):
        return f"Certyfikat {self.manufacturer.name} dla {self.technician}"

    class Meta:
        verbose_name = "Certyfikat"
        verbose_name_plural = "Certyfikaty"
        constraints = [
            models.UniqueConstraint(fields=['technician', 'manufacturer'], name='unique_technician_manufacturer_certification')
        ]
        indexes = [
            models.Index(fields=['manufacturer']),
            models.Index(fields=['technician']),
        ]
