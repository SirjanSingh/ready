from shop.pricing import apply_coupon


class Cart:
    def __init__(self):
        self.items = []

    def add(self, sku, price, qty=1):
        self.items.append((sku, price, qty))

    def total(self, coupon=None):
        subtotal = sum(p * q for _, p, q in self.items)
        return apply_coupon(subtotal, coupon) if coupon else subtotal
