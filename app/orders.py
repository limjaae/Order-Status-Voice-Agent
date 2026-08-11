"""
Order lookup logic.

This talks to a live Postgres database on Supabase instead of a local
file. The backend uses the service role key, which bypasses row level
security by design, since this is a trusted server calling the
database on the agent's behalf, not a customer's browser calling it
directly.
"""

import os
from typing import Optional

from supabase import create_client, Client

_client: Optional[Client] = None


def get_client() -> Client:
    """
    Create the Supabase client once and reuse it. Building a new client
    per request adds latency for no benefit, and on a voice call every
    extra hundred milliseconds is noticeable to the person on the phone.

    Env vars are read here rather than at module import time, so that
    importing this file (for example, when pytest collects tests that
    only exercise format_status_for_speech) doesn't crash in an
    environment where the database isn't configured yet.
    """
    global _client
    if _client is None:
        supabase_url = os.environ["SUPABASE_URL"]
        supabase_key = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
        _client = create_client(supabase_url, supabase_key)
    return _client


def find_order(order_number: Optional[str] = None, email: Optional[str] = None) -> Optional[dict]:
    """
    Look up an order by order number, or by email if the caller doesn't
    have their order number handy. Order number match takes priority
    since it's unambiguous, email is a fallback and returns the first
    match if a customer has placed more than one order.
    """
    client = get_client()

    if order_number:
        result = (
            client.table("orders")
            .select("*")
            .ilike("order_number", order_number.strip())
            .limit(1)
            .execute()
        )
        if result.data:
            return result.data[0]

    if email:
        result = (
            client.table("orders")
            .select("*")
            .ilike("email", email.strip())
            .limit(1)
            .execute()
        )
        if result.data:
            return result.data[0]

    return None


def format_status_for_speech(order: dict) -> str:
    """
    Turn an order record into a sentence the agent can say out loud.
    Keeping this separate from the lookup means we can tweak how it
    sounds without touching the database logic.
    """
    status = order["status"]

    if status == "processing":
        return (
            f"Your order is still being processed. "
            f"We expect it to ship with an estimated delivery around {order['estimated_delivery']}."
        )

    if status == "shipped":
        return (
            f"Your order has shipped with {order['carrier']}. "
            f"The tracking number is {order['tracking_number']}, "
            f"and it's estimated to arrive around {order['estimated_delivery']}."
        )

    if status == "delivered":
        return (
            f"Your order was delivered on {order['estimated_delivery']} "
            f"via {order['carrier']}."
        )

    return "I have your order pulled up, but I'm not able to read out its current status."
