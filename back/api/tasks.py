# api/tasks.py
from celery import shared_task
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import logging

from .models.devices import FiscalDevice
from .models.clients import Client

logger = logging.getLogger(__name__)


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, max_retries=5)
def send_device_inspection_reminder(self, device_id, trigger_user_id=None):
    """
    Wyślij e-mail przypomnienie o przeglądzie dla urządzenia fiskalnego.

    - device_id: PK obiektu FiscalDevice
    - trigger_user_id: opcjonalne id użytkownika, który wymusił wysyłkę (tylko dla logów)
    """
    try:
        device = FiscalDevice.objects.select_related('owner', 'brand').get(pk=device_id)
    except FiscalDevice.DoesNotExist:
        logger.warning("send_device_inspection_reminder: device %s does not exist", device_id)
        return False

    # Pobierz klienta (owner) i jego email
    client = device.owner  # zakładamy, że pole to Client
    recipient_email = getattr(client, 'email', None)

    if not recipient_email:
        logger.warning("send_device_inspection_reminder: device %s owner has no email", device_id)
        return False

    # --- Przygotuj pola zgodne z Twoim szablonem inspection_reminder.txt ---
    client_name = getattr(client, 'name', '') or getattr(client, 'company_name', '') or recipient_email
    brand_name = getattr(device.brand, 'name', '') if getattr(device, 'brand', None) else ''
    model_name = getattr(device, 'model_name', '') if hasattr(device, 'model_name') else ''
    device_brand_model = (brand_name + ' ' + model_name).strip() or 'Brak danych'

    # wybieramy numer unikatowy; dopasuj nazwę pola jeśli w modelu inna (unique_number / serial_number)
    device_unique_number = getattr(device, 'unique_number', None) or getattr(device, 'serial_number', None) or 'Brak danych'

    # daty: jeśli brak ostatniego przeglądu, pokaż 'Brak danych'
    last_service_date_obj = getattr(device, 'last_service_date', None)
    if last_service_date_obj:
        last_service_date = timezone.localtime(last_service_date_obj).strftime('%Y-%m-%d')
    else:
        last_service_date = 'Brak danych'

    # oblicz sugerowaną datę następnego przeglądu:
    # domyślnie SERVICE_INTERVAL_DAYS z settings lub 365 dni
    interval_days = int(getattr(settings, 'SERVICE_INTERVAL_DAYS', 365))
    if last_service_date_obj:
        next_service_date_obj = last_service_date_obj + timedelta(days=interval_days)
        next_service_date = timezone.localtime(next_service_date_obj).strftime('%Y-%m-%d')
    else:
        next_service_date = 'Proponowana: za {} dni'.format(interval_days)

    # Kontekst dla szablonu (zgodny z Twoim inspection_reminder.txt)
    context = {
        'client_name': client_name,
        'device_brand_model': device_brand_model,
        'device_unique_number': device_unique_number,
        'last_service_date': last_service_date,
        'next_service_date': next_service_date,
    }

    # Tytuł wiadomości (subject) — ustaw ręcznie, bo w pliku .txt masz linię "Temat: ..."
    subject = 'Przypomnienie o zbliżającym się przeglądzie urządzenia'

    # Renderuj tekstowy szablon (ten który podałeś)
    try:
        text_body = render_to_string('emails/inspection_reminder.txt', context)
    except Exception:
        # fallback - zrób prosty text z kontekstu (nie powinno się zdarzyć jeśli szablon istnieje)
        text_body = (
            f"Temat: {subject}\n\n"
            f"Witaj {client_name},\n\n"
            f"Marka i model: {device_brand_model}\n"
            f"Numer unikatowy: {device_unique_number}\n\n"
            f"Data ostatniego przeglądu: {last_service_date}\n"
            f"Sugerowana data następnego przeglądu: {next_service_date}\n\n"
            "Prosimy o kontakt w celu umówienia wizyty serwisanta.\n\n"
            "Z poważaniem,\nTwój Serwis Fiskalny"
        )

    # Spróbuj załadować html'owy odpowiednik, jeśli istnieje; jeśli nie - wygeneruj prosty html z text_body
    try:
        html_body = render_to_string('emails/inspection_reminder.html', context)
    except Exception:
        # prosty konwerter linii na <br/>
        html_body = "<html><body><pre style='font-family: sans-serif;'>" + (text_body.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')) + "</pre></body></html>"

    # Zbuduj i wyślij email
    msg = EmailMultiAlternatives(
        subject=subject,
        body=text_body,
        from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', settings.EMAIL_HOST_USER),
        to=[recipient_email],
    )
    msg.attach_alternative(html_body, "text/html")

    try:
        msg.send(fail_silently=False)
    except Exception as e:
        logger.exception("send_device_inspection_reminder: failed to send email for device %s to %s", device_id, recipient_email)
        # podnieś wyjątek aby Celery mógł retry'ować (autoretry_for działa)
        raise

    # Jeśli model urządzenia posiada pola do śledzenia przypomnień - zaktualizuj je bezpiecznie
    try:
        updated = False
        if hasattr(device, 'last_reminder_sent'):
            device.last_reminder_sent = timezone.now()
            updated = True
        if hasattr(device, 'reminder_count'):
            device.reminder_count = (device.reminder_count or 0) + 1
            updated = True
        if updated:
            device.save(update_fields=[f for f in ['last_reminder_sent', 'reminder_count'] if hasattr(device, f)])
    except Exception:
        logger.exception("send_device_inspection_reminder: failed to update reminder meta for device %s", device_id)

    logger.info("send_device_inspection_reminder: sent reminder for device %s to %s", device_id, recipient_email)
    return True


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, max_retries=3)
def send_email_task(self, subject, to_email, body, html_body=None):
    """
    Uniwersalne zadanie Celery do wysyłania e-maili.

    :param subject: Tytuł wiadomości e-mail.
    :param to_email: Adres odbiorcy (jako string lub lista stringów).
    :param body: Treść wiadomości w formacie tekstowym.
    :param html_body: Opcjonalna treść wiadomości w formacie HTML.
    """
    logger.info(f"Wysyłanie e-maila z tematem '{subject}' do {to_email}")

    # Upewnij się, że to_email jest listą
    if not isinstance(to_email, list):
        recipients = [to_email]
    else:
        recipients = to_email

    try:
        msg = EmailMultiAlternatives(
            subject=subject,
            body=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=recipients
        )

        if html_body:
            msg.attach_alternative(html_body, "text/html")

        msg.send(fail_silently=False)
        logger.info(f"E-mail do {to_email} został pomyślnie wysłany.")
        return True

    except Exception as e:
        logger.error(f"Nie udało się wysłać e-maila do {to_email}: {e}")
        # Dzięki autoretry_for, Celery automatycznie ponowi próbę w razie błędu
        raise self.retry(exc=e)
