# Case Study: Order Status Voice Agent

**A voice agent that answers order status calls, backed by a live database, built to prove out a pattern rather than just demo one.**

[Try it live](https://order-status-voice-agent-widget-jason-lims-projects-ef7a21ff.vercel.app) · [Source](https://github.com/limjaae/Order-Status-Voice-Agent)

---

## The problem

Order status is the single most repeated question in e-commerce support: high volume, low complexity, fully answerable from data a business already has. It's a good fit for a voice agent and a poor use of a human agent's time. I wanted to build the real thing, not a scripted demo, so I gave myself one constraint: every piece had to be live infrastructure, not mocked data.

## What I built

- **Voice layer:** ElevenLabs Conversational AI agent, handling speech-to-text, dialogue, and text-to-speech in one flow
- **Tool layer:** a custom webhook tool the agent calls mid-conversation to look up an order
- **Backend:** a FastAPI service deployed on Vercel, stateless, single responsibility
- **Data layer:** a live Postgres database on Supabase, with row-level security and scoped service-role permissions, not a JSON file pretending to be a database
- **Multi-tenant design:** the schema and lookup logic serve three separate demo storefronts through one shared table, proving the pattern scales past a single customer rather than being hardcoded to one
- **Multi-language:** English, German, Japanese, Korean, and Chinese, callers choose their language at the start of the call

## The architecture, in one line

Caller → ElevenLabs agent → `look_up_order` webhook → FastAPI backend → Supabase Postgres, and back out the same path as natural spoken language.

## What actually broke, and what fixing it took

The interesting part of this project wasn't the happy path, it was four real failures, each requiring a different kind of debugging:

**1. The tool existed but was never attached to the agent.** It showed up correctly in the workspace's tool library, but the agent's active configuration referenced zero tools. The agent would say "let me look that up," then quietly fabricate a plausible-sounding answer instead of failing loudly. Found by pulling the actual conversation transcript via the API and seeing `tool_calls: []` on every turn, not by guessing from symptoms.

**2. A correct API key, rejected as invalid.** Supabase had rolled out a new key format (`sb_secret_...`), but the pinned client library version predated support for it and validated keys client-side against the old JWT shape, rejecting a genuinely valid key before ever making a request. Confirmed by adding a temporary diagnostic endpoint that surfaced the real exception instead of a generic 500, then fixed by unpinning the dependency.

**3. Row-level security policies that weren't actually enough.** RLS policies control *which rows* a role can see, they don't grant *base table access* on their own. The service role could pass every policy check and still get `permission denied for table orders`, because the underlying `GRANT` had never been issued. An easy one to miss, and a good example of a security default that's stricter than it looks.

**4. A conversational agent tuned to interrupt too eagerly.** Default turn-taking settings caused the agent to cut off mid-sentence on any background noise and loop "are you still there?" indefinitely on silence. Fixed by tuning `turn_eagerness` and adding a real silence timeout, small parameters with an outsized effect on whether the thing feels usable.

Each of these needed a different diagnostic approach: reading raw conversation logs, adding temporary instrumentation to a production endpoint, reading a Postgres error's own hint text, and reasoning about conversational UX rather than code correctness. That range is closer to what integration work actually looks like than any single bug would have shown on its own.

## What I'd build next

- **Carrier API enrichment:** once an order is marked shipped, a second call to the relevant carrier's tracking API for live scan and location data, layering a real third-party enterprise integration on top of the owned database
- **Self-service documentation:** a guide for adding this pattern to a new store in under 20 minutes, written and available separately
- **Pre-call store selection:** passing store as a dynamic variable before the conversation starts, rather than asking for it conversationally, once the widget-side variable injection is verified

## Stack

ElevenLabs Conversational AI · Python · FastAPI · Supabase (Postgres) · Vercel · GitHub
