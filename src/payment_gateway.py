"""
Betalningsgateway – extern tjänst som kommunicerar med bank/kortleverantör.
I produktion gör detta riktiga HTTP-anrop mot en betaltjänst.
"""


class PaymentGateway:
    def charge(self, customer_id: str, amount: float) -> dict:
        """Drar pengar från kund. Returnerar ett kvitto-dict."""
        raise NotImplementedError("Kräver riktig bank-integration")