import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from ..models import Client

User = get_user_model()

pytestmark = pytest.mark.django_db


@pytest.fixture
def api_client():
    """
    Fixture, która tworzy instancję klienta API dla każdego testu.
    """
    return APIClient()


@pytest.fixture
def authenticated_client():
    """
    Fixture, która tworzy i zwraca zalogowanego klienta API.
    """
    user = User.objects.create_user(username='testuser', password='password123')
    client = APIClient()
    client.force_authenticate(user=user)
    return client


def test_get_clients_unauthenticated(api_client):
    """
    SCENARIUSZ: Niezalogowany użytkownik próbuje pobrać listę klientów.
    OCZEKIWANY REZULTAT: Odpowiedź 401 Unauthorized.
    """
    # Act
    response = api_client.get('/api/clients/')

    # Assert
    assert response.status_code == 401


def test_get_clients_authenticated(authenticated_client):
    """
    SCENARIUSZ: Zalogowany użytkownik pobiera listę klientów.
    OCZEKIWANY REZULTAT: Odpowiedź 200 OK.
    """
    # Arrange: stwórzmy jakiegoś klienta, żeby lista nie była pusta
    Client.objects.create(name="Klient 1", nip="1234567890")

    # Act
    response = authenticated_client.get('/api/clients/')

    # Assert
    assert response.status_code == 200
    assert len(response.data) == 1  # Sprawdzamy, czy w odpowiedzi jest 1 element
    assert response.data[0]['name'] == "Klient 1"


def test_create_client_authenticated(authenticated_client):
    """
    SCENARIUSZ: Zalogowany użytkownik tworzy nowego klienta.
    OCZEKIWANY REZULTAT: Odpowiedź 201 Created i klient istnieje w bazie.
    """
    # Arrange
    client_data = {
        "name": "Nowa Firma",
        "address": "Nowy Adres 1",
        "nip": "9876543210",
        "phone_number": "123-456-789",
        "email": "kontakt@nowafirma.pl"
    }

    # Act
    response = authenticated_client.post('/api/clients/', client_data)

    # Assert
    assert response.status_code == 201  # 201 Created to poprawny kod dla POST
    assert Client.objects.count() == 1
    assert Client.objects.get().name == "Nowa Firma"


def test_create_client_missing_required_field(authenticated_client):
    """
    SCENARIUSZ: Próba stworzenia klienta bez wymaganego pola 'name'.
    OCZEKIWANY REZULTAT: Odpowiedź 400 Bad Request.
    """
    # Arrange
    invalid_data = {
        "address": "Adres bez nazwy",
        "nip": "5555555555"
    }

    # Act
    response = authenticated_client.post('/api/clients/', invalid_data)

    # Assert
    assert response.status_code == 400
    assert 'name' in response.data  # Sprawdzamy, czy w odpowiedzi jest błąd dla pola 'name'