from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import secrets
import uuid
from .users import Company


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='orders')
    email = models.EmailField()
    stripe_session_id = models.CharField(max_length=255, blank=True, null=True, db_index=True)
    stripe_payment_intent = models.CharField(max_length=255, blank=True, null=True, db_index=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', db_index=True)
    amount_cents = models.PositiveIntegerField(null=True, blank=True)
    currency = models.CharField(max_length=10, default='PLN')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['stripe_session_id']),
            models.Index(fields=['stripe_payment_intent']),
        ]


class ActivationCode(models.Model):
    """
    One-time activation code. Company is accessible as activation.order.company.
    """
    code = models.CharField(max_length=64, unique=True, db_index=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='activation_codes')
    email = models.EmailField(null=True, blank=True)
    used = models.BooleanField(default=False, db_index=True)
    used_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        status = "used" if self.used else "active"
        return f"{self.code} ({status}) - {self.order.company.name if self.order and self.order.company else 'N/A'}"

    @classmethod
    def create_for_order(cls, order, email=None, lifetime_hours=48):
        code = secrets.token_urlsafe(16)
        expires = timezone.now() + timedelta(hours=lifetime_hours)
        return cls.objects.create(
            code=code,
            order=order,
            email=email,
            expires_at=expires
        )

    def redeem(self, user):
        if self.used:
            raise ValueError("Kod już został użyty")
        if self.expires_at and timezone.now() > self.expires_at:
            raise ValueError("Kod wygasł")
        self.used = True
        self.used_by = user
        self.save()
