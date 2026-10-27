FREE_OVER = 50.0
RATES = {"standard": 4.99, "express": 12.5}


def shipping_cost(subtotal: float, method: str = "standard") -> float:
    if subtotal > FREE_OVER:
        return 0.0
    return RATES[method]
