from shop.cart import Cart


def test_total():
    c = Cart()
    c.add("a", 10.0, 2)
    assert c.total() == 20.0
