from app.agent import process_cart_checkout, CARTS, DISCOUNT_CODES

def test_checkout_valid_no_discount():
    # Setup initial mock data for isolation
    CARTS["cart_test_1"] = {"user_id": "user_1", "items": [{"name": "Item A", "price": 50.0}]}

    result = process_cart_checkout(cart_id="cart_test_1", user_id="user_1")
    assert "Success" in result
    assert "Total: $50.00" in result

def test_checkout_valid_with_discount():
    CARTS["cart_test_2"] = {"user_id": "user_2", "items": [{"name": "Item B", "price": 100.0}]}
    DISCOUNT_CODES["TEST50"] = {"value": 50, "redeemed": False, "redeemed_by": None}

    result = process_cart_checkout(cart_id="cart_test_2", user_id="user_2", discount_code="TEST50")
    assert "Success" in result
    assert "Total: $50.00" in result
    assert DISCOUNT_CODES["TEST50"]["redeemed"] is True
    assert DISCOUNT_CODES["TEST50"]["redeemed_by"] == "user_2"

def test_checkout_invalid_user():
    CARTS["cart_test_3"] = {"user_id": "user_3", "items": [{"name": "Item C", "price": 10.0}]}

    result = process_cart_checkout(cart_id="cart_test_3", user_id="malicious_user")
    assert "Error" in result
    assert "does not belong to user" in result

def test_checkout_already_redeemed_discount():
    CARTS["cart_test_4"] = {"user_id": "user_4", "items": [{"name": "Item D", "price": 10.0}]}
    DISCOUNT_CODES["USED50"] = {"value": 50, "redeemed": True, "redeemed_by": "user_other"}

    result = process_cart_checkout(cart_id="cart_test_4", user_id="user_4", discount_code="USED50")
    assert "Error" in result
    assert "already been redeemed" in result

def test_checkout_nonexistent_cart():
    result = process_cart_checkout(cart_id="cart_nonexistent", user_id="user_5")
    assert "Error" in result
    assert "not found" in result

def test_checkout_empty_user():
    result = process_cart_checkout(cart_id="cart_test_1", user_id="")
    assert "Error" in result
    assert "valid user ID is required" in result
