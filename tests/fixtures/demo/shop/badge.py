from shop.cart import Cart


def render_badge(cart: Cart) -> str:
    return f"Cart ({cart.count()})"
