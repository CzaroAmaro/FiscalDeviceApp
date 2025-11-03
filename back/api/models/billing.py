from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import secrets
import uuid
from .users import Company  # import Twojego modelu Company

class Order(models.Model):
    """
    Model przechowujący zamówienie płatności Stripe.
    Każde zamówienie jest powiązane z firmą (Company).
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='orders')
    email = models.EmailField()  # email klienta/faktury
    stripe_session_id = models.CharField(max_length=255, blank=True, null=True, db_index=True)
    stripe_payment_intent = models.CharField(max_length=255, blank=True, null=True, db_index=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', db_index=True)
    amount_cents = models.PositiveIntegerField(null=True, blank=True)  # kwota w groszach
    currency = models.CharField(max_length=10, default='PLN')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['stripe_session_id']),
            models.Index(fields=['stripe_payment_intent']),
        ]

    def __str__(self):
        return f"Order {self.id} - {self.company.name} ({self.status})"


class ActivationCode(models.Model):
    """
    Jednorazowy kod aktywacyjny do rejestracji.
    Powiązany z firmą (Company) i z konkretnym Order.
    """
    code = models.CharField(max_length=64, unique=True, db_index=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='activation_codes')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='activation_codes')
    email = models.EmailField(null=True, blank=True)  # kod może być przypisany do maila
    used = models.BooleanField(default=False, db_index=True)
    used_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        status = "used" if self.used else "active"
        return f"{self.code} ({status}) - {self.company.name}"

    @classmethod
    def create_for_order(cls, order, email=None, lifetime_hours=48):
        """
        Tworzy nowy, losowy kod aktywacyjny dla danego zamówienia i firmy.
        """
        code = secrets.token_urlsafe(16)
        expires = timezone.now() + timedelta(hours=lifetime_hours)
        return cls.objects.create(
            code=code,
            order=order,
            company=order.company,
            email=email,
            expires_at=expires
        )

    def redeem(self, user):
        """
        Oznacza kod jako wykorzystany przez użytkownika.
        """
        if self.used:
            raise ValueError("Kod już został użyty")
        if self.expires_at and timezone.now() > self.expires_at:
            raise ValueError("Kod wygasł")
        self.used = True
        self.used_by = user
        self.save()
