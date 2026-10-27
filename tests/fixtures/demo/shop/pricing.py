COUPONS = {"TENOFF": 0.10, "FREESHIP": 0.0}
TAX_RATE = 0.18


def apply_coupon(subtotal: float, code: str) -> float:
    rate = COUPONS[code]
    return round(subtotal * (1 - rate), 2)


def add_tax(amount: float) -> float:
    return round(amount * (1 + TAX_RATE), 2)
