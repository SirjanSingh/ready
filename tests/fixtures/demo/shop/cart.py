from shop.inventory import reserve
from shop.pricing import add_tax, apply_coupon


class Cart:
    def __init__(self):
        self.items: list[tuple[str, float, int]] = []

    def add(self, sku: str, price: float, qty: int = 1) -> None:
        reserve(sku, qty)
        self.items.append((sku, price, qty))

    def count(self) -> int:
        return len(self.items)

    def total(self, coupon: str | None = None) -> float:
        subtotal = sum(p * q for _, p, q in self.items)
        if coupon:
            subtotal = apply_coupon(subtotal, coupon)
        return add_tax(subtotal)
