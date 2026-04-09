"""
Tester för OrderService med mock och stub.

Bibliotek: pytest + pytest-mock (wrapprar unittest.mock)
Kör med:  pytest tests/ -v

─────────────────────────────────────────────────────────────────────
STUB  – ersätter ett beroende med hårdkodade svar.
        Syftet är att styra vad SUT får tillbaka.
        Vi bryr oss INTE om hur stubben anropas.

MOCK  – ersätter ett beroende OCH verifiera att det anropas
        på rätt sätt (med rätt argument, rätt antal gånger).
        Syftet är att bekräfta att SUT beter sig korrekt.
─────────────────────────────────────────────────────────────────────
"""

import pytest
from unittest.mock import MagicMock, call
from src.order_service import OrderService, InsufficientFundsError


# ─────────────────────────────────────────────────────────────────────
# FIXTURES – skapar färska doubles inför varje test
# ─────────────────────────────────────────────────────────────────────

@pytest.fixture
def payment_stub():
    """
    STUB för PaymentGateway.
    Returnerar alltid ett lyckat kvitto – vi bryr oss inte om
    HUR den anropas, bara att OrderService FÅR rätt svar tillbaka.
    """
    stub = MagicMock()
    stub.charge.return_value = {
        "success": True,
        "transaction_id": "TXN-999",
    }
    return stub


@pytest.fixture
def email_stub():
    """
    STUB för EmailNotifier.
    Gör ingenting – vi vill bara att anropet inte kraschar.
    """
    return MagicMock()


@pytest.fixture
def service(payment_stub, email_stub):
    """Skapar en OrderService med stubbade beroenden."""
    return OrderService(payment_stub, email_stub)


# ─────────────────────────────────────────────────────────────────────
# TESTER SOM ANVÄNDER STUB
# Fokus: kontrollera returvärdet / tillståndet hos SUT
# ─────────────────────────────────────────────────────────────────────

class TestOrderServiceMedStub:
    def test_lyckad_order_returnerar_korrekt_struktur(self, service):
        """
        Stub-test: Vi kontrollerar att place_order returnerar
        rätt dict när betalningen lyckas.
        """
        resultat = service.place_order("KUND-1", "kund@example.com", 299.0)

        assert resultat["order_id"] == "TXN-999"
        assert resultat["customer_id"] == "KUND-1"
        assert resultat["amount"] == 299.0
        assert resultat["status"] == "confirmed"

    def test_negativt_belopp_kastar_valueerror(self, service):
        """
        Stub-test: OrderService ska kasta ValueError direkt,
        utan att ens nå PaymentGateway.
        """
        with pytest.raises(ValueError, match="positivt"):
            service.place_order("KUND-1", "kund@example.com", -50.0)

    def test_nekad_betalning_kastar_insufficientfundserror(self, payment_stub, email_stub):
        """
        Stub-test: Stubbens svar styr vilket exception SUT kastar.
        Stubben returnerar success=False → vi förväntar oss ett specifikt exception.
        """
        payment_stub.charge.return_value = {"success": False}
        service = OrderService(payment_stub, email_stub)

        with pytest.raises(InsufficientFundsError):
            service.place_order("KUND-1", "kund@example.com", 500.0)


# ─────────────────────────────────────────────────────────────────────
# TESTER SOM ANVÄNDER MOCK
# Fokus: verifiera att SUT kommunicerar rätt med sina beroenden
# ─────────────────────────────────────────────────────────────────────

class TestOrderServiceMedMock:
    def test_betalning_anropas_med_ratt_argument(self, payment_stub, email_stub):
        """
        MOCK-test: Verifierar att charge() anropas med exakt
        rätt customer_id och belopp.

        Det räcker inte att returvärdet blir rätt – vi vill veta
        att SUT faktiskt kommunicerade korrekt med sin gateway.
        """
        payment_mock = payment_stub   # MagicMock spelar båda rollerna
        service = OrderService(payment_mock, email_stub)

        service.place_order("KUND-42", "kund@example.com", 149.0)

        # Assertion mot mocken: HUR anropades den?
        payment_mock.charge.assert_called_once_with("KUND-42", 149.0)

    def test_epost_skickas_med_ratt_data(self, payment_stub, email_stub):
        """
        MOCK-test: Verifierar att send_confirmation() anropas
        med rätt e-postadress, order-id och belopp.
        """
        email_mock = email_stub
        service = OrderService(payment_stub, email_mock)

        service.place_order("KUND-42", "kund@example.com", 149.0)

        email_mock.send_confirmation.assert_called_once_with(
            "kund@example.com", "TXN-999", 149.0
        )

    def test_epost_skickas_inte_vid_nekad_betalning(self, payment_stub, email_stub):
        """
        MOCK-test: Om betalningen nekas ska INGET bekräftelsemejl skickas.
        Detta är ett beteendekrav som bara en mock kan verifiera.
        """
        payment_stub.charge.return_value = {"success": False}
        email_mock = email_stub
        service = OrderService(payment_stub, email_mock)

        with pytest.raises(InsufficientFundsError):
            service.place_order("KUND-1", "kund@example.com", 999.0)

        # Mocken bekräftar: send_confirmation anropades ALDRIG
        email_mock.send_confirmation.assert_not_called()

    def test_betalning_anropas_exakt_en_gang(self, payment_stub, email_stub):
        """
        MOCK-test: Verifierar att charge() inte anropas flera gånger
        för en och samma order (viktigt för att undvika dubbeldebiteringar).
        """
        payment_mock = payment_stub
        service = OrderService(payment_mock, email_stub)

        service.place_order("KUND-1", "kund@example.com", 200.0)

        assert payment_mock.charge.call_count == 1