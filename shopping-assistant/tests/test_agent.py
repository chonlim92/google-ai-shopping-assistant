from app.agent import redeem_discount, DISCOUNT_CODES

def test_redeem_discount_empty_user():
    # Attempt redemption with empty user_id
    result = redeem_discount(code="WELCOME50", user_id="")
    assert "Error" in result
    assert "A valid user ID is required" in result

def test_redeem_discount_invalid_code():
    # Attempt redemption with invalid discount code
    result = redeem_discount(code="INVALIDCODE", user_id="user1")
    assert "Error" in result
    assert "is invalid" in result

def test_redeem_discount_already_redeemed():
    # Setup test record as already redeemed
    DISCOUNT_CODES["REDEEMED50"] = {"value": 50, "redeemed": True, "redeemed_by": "user1"}

    result = redeem_discount(code="REDEEMED50", user_id="user2")
    assert "Error" in result
    assert "has already been redeemed" in result

def test_redeem_discount_success():
    # Setup clean code
    DISCOUNT_CODES["CLEAN50"] = {"value": 50, "redeemed": False, "redeemed_by": None}

    result = redeem_discount(code="CLEAN50", user_id="user3")
    assert "Success" in result
    assert "successfully redeemed" in result
    assert DISCOUNT_CODES["CLEAN50"]["redeemed"] is True
    assert DISCOUNT_CODES["CLEAN50"]["redeemed_by"] == "user3"
