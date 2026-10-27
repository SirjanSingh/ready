from shop.shipping import shipping_cost


def test_standard_under_threshold():
    assert shipping_cost(20.0) == 4.99


def test_free_over_threshold():
    assert shipping_cost(80.0) == 0.0
