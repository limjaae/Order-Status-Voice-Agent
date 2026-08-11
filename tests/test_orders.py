"""
Tests for the speech formatting logic.

These only test format_status_for_speech, which is pure logic with no
database call. The lookup function itself talks to a live Supabase
database, so testing it here would mean either hitting production data
in a test run or maintaining a second test database. For a project
this size, that trade off isn't worth it yet, this is one to revisit
if the project grows past a solo demo.
"""

from app.orders import format_status_for_speech


def make_order(**overrides):
    base = {
        "status": "processing",
        "carrier": None,
        "tracking_number": None,
        "estimated_delivery": "2026-08-14",
    }
    base.update(overrides)
    return base


def test_format_status_for_processing_order():
    order = make_order(status="processing")
    message = format_status_for_speech(order)
    assert "processed" in message
    assert order["estimated_delivery"] in message


def test_format_status_for_shipped_order():
    order = make_order(status="shipped", carrier="UPS", tracking_number="1Z999AA10123456784")
    message = format_status_for_speech(order)
    assert "UPS" in message
    assert "1Z999AA10123456784" in message


def test_format_status_for_delivered_order():
    order = make_order(status="delivered", carrier="FedEx")
    message = format_status_for_speech(order)
    assert "delivered" in message
    assert "FedEx" in message


def test_format_status_for_unknown_status_does_not_crash():
    order = make_order(status="cancelled")
    message = format_status_for_speech(order)
    assert isinstance(message, str)
    assert len(message) > 0
