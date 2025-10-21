import pytest
from ..models import Client, FiscalDevice, CustomUser

pytestmark = pytest.mark.django_db

def test_client_creation_and_str():
    """
    Testuje tworzenie obiektu Klienta i jego reprezentację tekstową.
    """
    client = Client.objects.create(
        name="Testowa Firma Sp. z o.o.",
        address="ul. Testowa 1, 00-001 Warszawa",
        nip="1234567890"
    )

    retrieved_client = Client.objects.get(id=client.id)
    str_representation = str(retrieved_client)

    assert retrieved_client.name == "Testowa Firma Sp. z o.o."
    assert str_representation == "Testowa Firma Sp. z o.o. (NIP: 1234567890)"


def test_fiscal_device_creation():
    """
    Testuje tworzenie obiektu Urządzenia Fiskalnego i jego relację z Klientem.
    """
    # Arrange
    client = Client.objects.create(name="Właściciel Urządzenia", nip="1112223344")
    user = CustomUser.objects.create_user(username="testuser")

    device = FiscalDevice.objects.create(
        brand_name="Novitus",
        model_name="Nano E",
        unique_number="NOV12345UNIQUE",
        serial_number="SN12345",
        sale_date="2024-01-15",
        owner=client
    )

    # Act
    retrieved_device = FiscalDevice.objects.get(id=device.id)
    str_representation = str(retrieved_device)

    # Assert
    assert retrieved_device.brand_name == "Novitus"
    assert retrieved_device.owner.name == "Właściciel Urządzenia"
    assert str(retrieved_device.owner) == "Właściciel Urządzenia (NIP: 1112223344)"
    assert str_representation == "Nano E - S/N: SN12345"