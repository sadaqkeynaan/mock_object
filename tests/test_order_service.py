import pytest
from unittest.mock import MagicMock
from src.order_service import OrderService, InsufficientFundsError


@pytest.fixture
def payment_stub():
    stub = MagicMock()
    stub.charge.return_value = {
        "success": True,
        "transaction_id": "TXN-999",
    }
    return stub


@pytest.fixture
def email_stub():
    return MagicMock()


@pytest.fixture
def service(payment_stub, email_stub):
    return OrderService(payment_stub, email_stub)


class TestOrderServiceMedStub:
    def test_lyckad_order_returnerar_korrekt_struktur(self, service):
        resultat = service.place_order("KUND-1", "kund@example.com", 299.0)

        assert resultat["order_id"] == "TXN-999"
        assert resultat["customer_id"] == "KUND-1"
        assert resultat["amount"] == 299.0
        assert resultat["status"] == "confirmed"

    def test_negativt_belopp_kastar_valueerror(self, service):
        with pytest.raises(ValueError, match="positivt"):
            service.place_order("KUND-1", "kund@example.com", -50.0)

    def test_nekad_betalning_kastar_insufficientfundserror(self, payment_stub, email_stub):
        payment_stub.charge.return_value = {"success": False}
        service = OrderService(payment_stub, email_stub)

        with pytest.raises(InsufficientFundsError):
            service.place_order("KUND-1", "kund@example.com", 500.0)


class TestOrderServiceMedMock:
    def test_betalning_anropas_med_ratt_argument(self, payment_stub, email_stub):
        payment_mock = payment_stub
        service = OrderService(payment_mock, email_stub)

        service.place_order("KUND-42", "kund@example.com", 149.0)

        payment_mock.charge.assert_called_once_with("KUND-42", 149.0)

    def test_epost_skickas_med_ratt_data(self, payment_stub, email_stub):
        email_mock = email_stub
        service = OrderService(payment_stub, email_mock)

        service.place_order("KUND-42", "kund@example.com", 149.0)

        email_mock.send_confirmation.assert_called_once_with(
            "kund@example.com", "TXN-999", 149.0
        )

    def test_epost_skickas_inte_vid_nekad_betalning(self, payment_stub, email_stub):
        payment_stub.charge.return_value = {"success": False}
        email_mock = email_stub
        service = OrderService(payment_stub, email_mock)

        with pytest.raises(InsufficientFundsError):
            service.place_order("KUND-1", "kund@example.com", 999.0)

        email_mock.send_confirmation.assert_not_called()

    def test_betalning_anropas_exakt_en_gang(self, payment_stub, email_stub):
        payment_mock = payment_stub
        service = OrderService(payment_mock, email_stub)

        service.place_order("KUND-1", "kund@example.com", 200.0)

        assert payment_mock.charge.call_count == 1