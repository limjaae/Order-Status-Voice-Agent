"""
Support ticket creation.

Used by the escalation agent, not the primary order-status agent. When
the primary agent can't find an order, it transfers the caller to the
escalation agent, which gathers details and files a ticket here. This
makes the handoff a real recorded action rather than a spoken promise
with no backend effect.
"""

from typing import Optional

from app.orders import get_client


def create_ticket(
    store: str,
    issue_summary: str,
    order_number: Optional[str] = None,
    email: Optional[str] = None,
) -> dict:
    """
    Insert a support ticket row and return it, including its id, which
    doubles as the reference number read back to the caller.
    """
    client = get_client()
    result = (
        client.table("support_tickets")
        .insert({
            "store": store,
            "order_number": order_number,
            "email": email,
            "issue_summary": issue_summary,
        })
        .execute()
    )
    return result.data[0]
