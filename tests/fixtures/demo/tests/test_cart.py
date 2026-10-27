from shop.cart import Cart


def test_total_with_tax():
    c = Cart()
    c.add("tee", 10.0, 2)
    assert c.total() == 23.6
