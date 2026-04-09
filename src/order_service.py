"""
OrderService – applikationslogiken vi vill testa.

Ansvarar för att:
  1. Ta betalt via PaymentGateway
  2. Skicka bekräftelse via EmailNotifier
  3. Returnera ett strukturerat orderresultat

Detta är koden vi faktiskt testar (System Under Test = SUT).
"""

from src.payment_gateway import PaymentGateway
from src.email_notifier import EmailNotifier


class InsufficientFundsError(Exception):
    pass


class OrderService:
    def __init__(self, payment_gateway: PaymentGateway, email_notifier: EmailNotifier):
        # Beroenden injiceras via konstruktorn (Dependency Injection)
        # Detta gör det enkelt att byta ut mot mocks i tester
        self._payment = payment_gateway
        self._notifier = email_notifier

    def place_order(self, customer_id: str, email: str, amount: float) -> dict:
        """
        Lägger en order:
          - Validerar beloppet
          - Drar betalning via gateway
          - Skickar bekräftelsemejl
          - Returnerar orderdetaljer
        """
        if amount <= 0:
            raise ValueError("Belopp måste vara positivt")

        # Anropa extern betaltjänst
        receipt = self._payment.charge(customer_id, amount)

        if not receipt.get("success"):
            raise InsufficientFundsError("Betalningen nekades")

        order_id = receipt["transaction_id"]

        # Skicka bekräftelsemejl
        self._notifier.send_confirmation(email, order_id, amount)

        return {
            "order_id": order_id,
            "customer_id": customer_id,
            "amount": amount,
            "status": "confirmed",
        }