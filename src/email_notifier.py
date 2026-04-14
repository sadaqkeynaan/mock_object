class EmailNotifier:
    def send_confirmation(self, email: str, order_id: str, amount: float) -> None:
        raise NotImplementedError("Kräver riktig e-posttjänst")