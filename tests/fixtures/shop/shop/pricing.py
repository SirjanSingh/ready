COUPONS = {"TENOFF": 0.10}


def apply_coupon(subtotal, code):
    rate = COUPONS[code]
    return round(subtotal * (1 - rate), 2)
