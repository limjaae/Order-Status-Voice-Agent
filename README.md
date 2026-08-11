# Order Status Voice Agent

A small voice agent that answers one question well: where is my order.

It picks up a call, asks for an order number or checkout email, looks it up against a live database, and tells the customer where things stand in plain spoken language, in their own language.

## Why this exists

Order status is the single most repeated question in e-commerce support. It is high volume and low complexity, which makes it a good fit for a voice agent and a poor use of a support rep's time. This project is a narrow, working version of that idea, built end to end with real infrastructure rather than mocked up.

## How it works

1. A customer calls a phone number connected to the agent.
2. The agent greets them and asks for an order number or checkout email.
3. A FastAPI service looks the order up in a live Postgres database on Supabase.
4. The agent reads the status back naturally: processing, shipped with a tracking number, or delivered.
5. If nothing matches, the agent asks once more, then offers to hand off to a human.

The voice side, meaning speech in, speech out, and conversation handling, runs on ElevenLabs Conversational AI. The lookup itself is a small custom tool the agent calls mid conversation.

## Languages

The agent runs in English by default, with German, Japanese, Korean, and Chinese added as additional languages in the ElevenLabs dashboard. Callers are asked for their preferred language at the start of the call, and it stays fixed for that call.

## Project layout

```
order-status-voice-agent/
  app/
    main.py           FastAPI app exposing the order lookup tool as a webhook
    orders.py          Live database lookup logic
    agent_config.py     System prompt, tool schema, and language setup notes
  tests/
    test_orders.py       Tests for the speech formatting logic
  requirements.txt
  .env.example
```

## Running it locally

```bash
pip install -r requirements.txt
cp .env.example .env
# fill in SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY, ELEVENLABS_API_KEY
uvicorn app.main:app --reload
```

The webhook will be live at `http://localhost:8000/lookup-order`. Point an ElevenLabs Conversational AI agent's custom tool at that URL, using the tool schema in `app/agent_config.py`.

## What this is not

This is a scoped project, not a full support platform. It handles order status only, not changes, cancellations, or refunds. Ten seed orders live in the database to make it demoable end to end, real order data would replace them the same way any other row would be inserted.
