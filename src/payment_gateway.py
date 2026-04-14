class PaymentGateway:
    def charge(self, customer_id: str, amount: float) -> dict:
        raise NotImplementedError("Kräver riktig bank-integration")