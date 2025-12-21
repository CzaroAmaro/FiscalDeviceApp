from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.db import transaction

from .models.tickets import ServiceTicket
from .models.devices import FiscalDevice, DeviceHistoryEntry


@receiver(pre_save, sender=ServiceTicket)
def capture_previous_ticket_state(sender, instance, **kwargs):
    if instance.pk:
        try:
            old_instance = ServiceTicket.objects.get(pk=instance.pk)
            instance._previous_status = old_instance.status
            instance._previous_device_id = old_instance.device_id
        except ServiceTicket.DoesNotExist:
            instance._previous_status = None
            instance._previous_device_id = None
    else:
        instance._previous_status = None
        instance._previous_device_id = None


@receiver(post_save, sender=ServiceTicket)
def update_device_status_on_ticket_change(sender, instance, created, **kwargs):
    previous_status = getattr(instance, '_previous_status', None)
    previous_device_id = getattr(instance, '_previous_device_id', None)
    current_status = instance.status
    current_device = instance.device

    if not created and previous_status == current_status and previous_device_id == (
    current_device.id if current_device else None):
        return

    devices_to_update = set()

    if current_device:
        devices_to_update.add(current_device.id)

    if previous_device_id and previous_device_id != (current_device.id if current_device else None):
        devices_to_update.add(previous_device_id)

    with transaction.atomic():
        for device_id in devices_to_update:
            try:
                device = FiscalDevice.objects.select_for_update().get(id=device_id)
            except FiscalDevice.DoesNotExist:
                continue

            has_active_tickets = ServiceTicket.objects.filter(
                device_id=device_id,
                status__in=[ServiceTicket.Status.OPEN, ServiceTicket.Status.IN_PROGRESS]
            ).exists()

            old_device_status = device.status
            new_device_status = None

            if has_active_tickets:
                if device.status not in [FiscalDevice.Status.SERVICED, FiscalDevice.Status.DECOMMISSIONED]:
                    new_device_status = FiscalDevice.Status.SERVICED
            else:
                if device.status == FiscalDevice.Status.SERVICED:
                    new_device_status = FiscalDevice.Status.ACTIVE

            if new_device_status and new_device_status != old_device_status:
                device.status = new_device_status
                device.save(update_fields=['status'])

                if new_device_status == FiscalDevice.Status.SERVICED:
                    description = f"Status urządzenia zmieniony automatycznie na 'W serwisie' z powodu aktywnego zgłoszenia serwisowego."
                else:
                    description = f"Status urządzenia przywrócony automatycznie na 'Aktywne' po zamknięciu wszystkich zgłoszeń serwisowych."

                DeviceHistoryEntry.objects.create(
                    device=device,
                    action_type=DeviceHistoryEntry.ActionType.STATUS_CHANGED,
                    description=description,
                    actor=None
                )


@receiver(post_save, sender=ServiceTicket)
def log_ticket_creation_to_device_history(sender, instance, created, **kwargs):
    if created and instance.device:
        action_type = getattr(
            DeviceHistoryEntry.ActionType,
            'TICKET_CREATED',
            DeviceHistoryEntry.ActionType.STATUS_CHANGED
        )

        DeviceHistoryEntry.objects.create(
            device=instance.device,
            action_type=action_type,
            description=f"Utworzono nowe zgłoszenie serwisowe nr {instance.ticket_number} ('{instance.title}').",
            actor=None
        )