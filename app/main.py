"""
Webhook server for the Order Status Voice Agent.

The ElevenLabs agent calls this service mid-conversation whenever it
needs to look up an order. This file just wires the HTTP layer to the
lookup logic in orders.py, it doesn't contain any conversation logic
itself, that lives in the agent's system prompt.
"""

from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional

from app.orders import find_order, format_status_for_speech

app = FastAPI(title="Order Status Voice Agent")


class LookupRequest(BaseModel):
    order_number: Optional[str] = None
    email: Optional[str] = None
    store: Optional[str] = None


class LookupResponse(BaseModel):
    found: bool
    message: str


@app.get("/")
def root():
    """
    A bare visit to the base URL isn't a real use of this API, but it
    shouldn't look broken either. This exists so a person clicking the
    deployment link gets a helpful pointer instead of a raw 404.
    """
    return {
        "service": "Order Status Voice Agent",
        "status": "running",
        "endpoints": ["/health", "/lookup-order"]
    }


@app.get("/health")
def health_check():
    """Simple check so you can confirm the service is up before wiring the agent to it."""
    return {"status": "ok"}


@app.post("/lookup-order", response_model=LookupResponse)
def lookup_order(request: LookupRequest):
    """
    Look up an order and return a spoken-friendly status message.
    Always returns 200, even on a miss, since the agent needs to keep
    the conversation going either way rather than handling an HTTP error.
    """
    order = find_order(order_number=request.order_number, email=request.email, store=request.store)

    if order is None:
        return LookupResponse(
            found=False,
            message="I couldn't find an order matching that. Could you double check the order number?"
        )

    return LookupResponse(
        found=True,
        message=format_status_for_speech(order)
    )
