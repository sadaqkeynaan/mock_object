from src.payment_gateway import PaymentGateway
from src.email_notifier import EmailNotifier


class InsufficientFundsError(Exception):
    pass


class OrderService:
    def __init__(self, payment_gateway: PaymentGateway, email_notifier: EmailNotifier):
        self._payment = payment_gateway
        self._notifier = email_notifier

    def place_order(self, customer_id: str, email: str, amount: float) -> dict:
        if amount <= 0:
            raise ValueError("Belopp måste vara positivt")

        receipt = self._payment.charge(customer_id, amount)

        if not receipt.get("success"):
            raise InsufficientFundsError("Betalningen nekades")

        order_id = receipt["transaction_id"]

        self._notifier.send_confirmation(email, order_id, amount)

        return {
            "order_id": order_id,
            "customer_id": customer_id,
            "amount": amount,
            "status": "confirmed",
        }