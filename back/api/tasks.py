from celery import shared_task
import time

# Dekorator @shared_task sprawia, że ta funkcja jest "zadaniem" Celery
@shared_task
def add(x, y):
    print(f"Otrzymano zadanie: {x} + {y}")
    time.sleep(5)  # Symulujemy długie zadanie (np. wysyłanie maila, generowanie PDF)
    result = x + y
    print(f"Zadanie zakończone. Wynik: {result}")
    return result