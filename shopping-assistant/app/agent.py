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


root_agent = Agent(
    name="shopping_assistant",
    model=Gemini(
        model="gemini-2.5-flash",
        api_key=api_key,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=(
        "You are an AI Shopping Assistant for a retail store. Help customers find products, "
        "answer questions, and assist in redeeming discount codes using the 'redeem_discount' tool. "
        "Always request their registered User ID when they ask to redeem a discount code."
    ),
    tools=[redeem_discount],
)

app = App(
    root_agent=root_agent,
    name="shopping_assistant_app",
)
