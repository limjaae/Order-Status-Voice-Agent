# Add Voice Order Status to Your Store in About 20 Minutes

A guide to standing up your own version of this pattern: a voice agent that answers "where is my order," backed by your own live database. Written from the actual build, including the mistakes that cost the most time, so you don't repeat them.

## What you'll have at the end

A phone- or browser-accessible voice agent that looks up real order data and reads the status back naturally, with no support rep involved for the common case.

## Prerequisites

- An ElevenLabs account (free tier is enough to build and test)
- A Postgres database, Supabase is used here, but any Postgres host works
- Somewhere to deploy a small backend, Vercel is used here, any host that runs Python works

## Step 1: Set up your table

At minimum, your orders table needs an order number, a lookup key like email, a status, and whatever detail you want read back (tracking number, carrier, delivery estimate). Two things worth doing from the start, not after something breaks:

```sql
alter table public.orders enable row level security;

create policy "Service role can read orders"
    on public.orders
    for select
    to service_role
    using (true);

-- This step is easy to miss and won't show up as an error until your
-- backend actually tries to query the table. RLS policies control
-- which rows a role can see, they don't grant base table access.
-- Both are required.
grant select on public.orders to service_role;
```

If you skip the `grant`, everything looks correctly configured and you'll get `permission denied for table orders` the first time your backend actually queries it, with no earlier warning.

## Step 2: Build the lookup backend

A single endpoint is enough: accept a POST request with whatever identifiers you support (order number, email), query your database, return a short natural-language string. Keep the response text short and speech-shaped, not JSON echoed back as a sentence, this is what the agent will actually say out loud.

**Use a current version of your database client library.** If you're on Supabase specifically: they've rolled out a new API key format (`sb_secret_...`). Older client library versions validate keys client-side against the old format and will reject a completely valid key with a generic "Invalid API key" error that gives no indication the key itself is fine. Pin to a recent version, not whatever a tutorial from a year ago tells you to use.

## Step 3: Create the agent

In the ElevenLabs dashboard, create a Conversational AI agent. Write a short, tightly scoped system prompt: what the agent's job is, what it should ask for, how it should read results back, and explicitly what it should refuse to do (order changes, refunds, anything outside lookup).

## Step 4: Attach your tool, and verify it actually attached

Add your backend as a custom webhook tool under the agent's Tools section. **This is the step most likely to silently fail.** A tool can exist correctly in your workspace's tool library and still not be attached to any specific agent, there's a difference between the tool existing and the tool being usable by this agent. If your agent ever says something like "let me check that" and then gives a suspiciously fluent, slightly-wrong answer instead of an actual error, this is the first thing to check, not a prompt problem.

To verify: pull a real conversation transcript after a test call and check whether `tool_calls` is actually populated on the agent's turns, not just present in the workspace tool list.

## Step 5: Tune turn-taking before you call it done

Default conversational settings are often tuned to feel responsive in a demo, which translates to feeling trigger-happy on a real call, cutting in on background noise, or looping "are you still there?" during normal pauses. Two settings worth adjusting immediately:

- `turn_eagerness`: set to a more patient value if the agent interrupts too readily
- `silence_end_call_timeout`: set an actual value, an unset or disabled timeout means the agent nudges the caller indefinitely instead of ending the call gracefully

## Step 6: Test with real failure cases, not just the happy path

Test an order that exists, one that doesn't, and one where you deliberately mumble or pause mid-sentence. The gaps show up in the second and third cases, not the first.

## Common failure signature, quick reference

| Symptom | Likely cause |
|---|---|
| Agent gives a fluent but wrong answer | Tool exists but isn't attached to the agent |
| Backend returns 500 with no clear reason in logs | Add a temporary debug endpoint that returns the real exception, don't guess from truncated logs |
| "Invalid API key" despite a correct key | Client library version predates your database provider's current key format |
| "Permission denied" despite RLS configured | RLS policy exists, but base table `GRANT` was never issued |
| Agent talks over you or loops "still there?" | Turn-taking settings need tuning, not the system prompt |

## Where to take this further

Add more identifying fields (phone, order + zip) for verification, extend to real carrier tracking APIs once an order ships, or scope one deployment to multiple storefronts through a single shared table rather than standing up separate infrastructure per brand.
