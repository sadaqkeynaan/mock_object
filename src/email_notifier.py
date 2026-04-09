"""
E-postnotifierare – extern tjänst som skickar e-post via t.ex. SendGrid.
I produktion skickar detta riktiga e-postmeddelanden.
"""


class EmailNotifier:
    def send_confirmation(self, email: str, order_id: str, amount: float) -> None:
        """Skickar orderbekräftelse till kund."""
        raise NotImplementedError("Kräver riktig e-posttjänst")