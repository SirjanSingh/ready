STOCK = {"tee": 5, "mug": 2, "cap": 0}


class OutOfStock(Exception):
    pass


def reserve(sku: str, qty: int) -> None:
    if STOCK.get(sku, 0) < qty:
        raise OutOfStock(sku)
    STOCK[sku] -= qty
