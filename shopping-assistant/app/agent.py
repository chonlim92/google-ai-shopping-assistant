# ruff: noqa
import os
from typing import Dict, Optional
from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models import Gemini
from google.genai import types

# Simulated hardcoded API Key for security demonstration
api_key = "AIzaSyD-mock-key-value-12345"

# Setup Google AI Studio API Key Authentication
os.environ["GOOGLE_GENAI_USE_ENTERPRISE"] = "FALSE"

# In-memory database of single-use discount codes and their redemption records
DISCOUNT_CODES = {
    "WELCOME50": {"value": 50, "redeemed": False, "redeemed_by": None},
    "SUMMER20": {"value": 20, "redeemed": False, "redeemed_by": None},
}

# In-memory database of active customer shopping carts
CARTS = {
    "cart_123": {
        "user_id": "user_abc",
        "items": [{"name": "Premium Jacket", "price": 100.0}],
    },
    "cart_456": {
        "user_id": "user_xyz",
        "items": [{"name": "Running Shoes", "price": 80.0}, {"name": "Socks", "price": 10.0}],
    },
}


def redeem_discount(code: str, user_id: str) -> str:
    """Redeems a single-use discount code for a registered user.

    Args:
        code: The discount code to redeem (e.g., WELCOME50, SUMMER20).
        user_id: The unique ID of the registered user.

    Returns:
        A success or error message detailing the result of the redemption.
    """
    code_upper = code.strip().upper()
    user_id_clean = user_id.strip()

    if not user_id_clean:
        return "Error: A valid user ID is required to redeem a discount code."

    if code_upper not in DISCOUNT_CODES:
        return f"Error: Discount code '{code}' is invalid."

    record = DISCOUNT_CODES[code_upper]
    if record["redeemed"]:
        return f"Error: Discount code '{code}' has already been redeemed by user '{record['redeemed_by']}'."

    # Process redemption
    record["redeemed"] = True
    record["redeemed_by"] = user_id_clean
    return f"Success: Discount code '{code}' of {record['value']}% has been successfully redeemed for user '{user_id_clean}'."


def process_cart_checkout(
    cart_id: str, user_id: str, discount_code: Optional[str] = None
) -> str:
    """Processes checkout for a given cart, optionally applying a discount code.

    Args:
        cart_id: The ID of the cart to checkout.
        user_id: The ID of the registered user checking out.
        discount_code: An optional discount code to apply.

    Returns:
        A message detailing the checkout total and order confirmation status.
    """
    c_id = cart_id.strip()
    u_id = user_id.strip()

    if not u_id:
        return "Error: A valid user ID is required to process checkout."

    if c_id not in CARTS:
        return f"Error: Cart '{cart_id}' not found."

    cart = CARTS[c_id]
    if cart["user_id"] != u_id:
        return f"Error: Cart '{cart_id}' does not belong to user '{user_id}'."

    # Calculate base price
    base_price = sum(item["price"] for item in cart["items"])
    discount_amount = 0.0

    if discount_code:
        code_upper = discount_code.strip().upper()
        if code_upper not in DISCOUNT_CODES:
            return f"Error: Discount code '{discount_code}' is invalid."

        record = DISCOUNT_CODES[code_upper]
        if record["redeemed"]:
            return f"Error: Discount code '{discount_code}' has already been redeemed by user '{record['redeemed_by']}'."

        # Apply discount
        discount_amount = base_price * (record["value"] / 100.0)
        record["redeemed"] = True
        record["redeemed_by"] = u_id

    final_price = max(0.0, base_price - discount_amount)

    # Process order
    items_list = ", ".join(item["name"] for item in cart["items"])
    return f"Success: Order processed for user '{u_id}'. Items: {items_list}. Total: ${final_price:.2f} (Base: ${base_price:.2f}, Discount applied: ${discount_amount:.2f})."


root_agent = Agent(
    name="shopping_assistant",
    model=Gemini(
        model="gemini-2.5-flash",
        api_key=api_key,  # type: ignore
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=(
        "You are an AI Shopping Assistant for a retail store. Help customers find products, "
        "answer questions, and assist in redeeming discount codes and checking out shopping carts "
        "using the 'redeem_discount' and 'process_cart_checkout' tools. "
        "Always request their registered User ID when they ask to redeem a discount code or check out."
    ),
    tools=[redeem_discount, process_cart_checkout],
)

app = App(
    root_agent=root_agent,
    name="shopping_assistant_app",
)
