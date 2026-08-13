# PRD: Order Status Voice Agent

**Status: live.** This reflects what's actually built and running, not the original scoped plan. Where something changed from the first draft, it's noted.

## Problem

Order status is the single most repeated question in e-commerce support: high volume, low complexity, fully answerable from data a business already has. It's a good fit for a voice agent and a poor use of a human agent's time.

## Target User

Two distinct users, worth naming separately since they shaped different parts of the build:

- **The end customer**: someone calling to ask where their order is, in one of five languages, without navigating a phone menu.
- **The recruiter or engineer evaluating this project**: someone with 30–90 seconds to decide whether this demonstrates real integration and architecture skill, not just a scripted demo.

## Core User Flow

1. Caller opens the web widget or dials in.
2. Agent greets them and asks which store they ordered from (Bondi & Co, Southbank Supply, or Redgum Traders).
3. Caller states a preferred language if not English; the agent has presets for German, Japanese, Korean, and Chinese.
4. Agent asks for an order number or checkout email.
5. Agent calls the `look_up_order` tool with store, plus order number or email.
6. Tool queries a live Postgres table on Supabase, scoped to that store.
7. Agent reads the result back in natural spoken language: processing, shipped with carrier and tracking number, or delivered.
8. On no match, the agent asks once more, then says it will hand off to a team member. **No real handoff exists yet** — this is spoken only, not a functional transfer. Flagged here so it isn't mistaken for a finished feature.

## Success Metric

Original metric was: 8 of 10 test calls resolve correctly without human handoff. Revised, since a fixed test-call count doesn't reflect what actually mattered building this:

- The full path (voice → tool → live database → spoken response) works end to end, verified against real Supabase rows, not mocked data.
- Every major failure encountered while building it was found and fixed, not worked around: a tool that was silently never attached to the agent, a valid API key rejected by an outdated client library, RLS policies configured but base table grants missing, and turn-taking settings tuned for natural conversation instead of interrupting or looping.
- The project is legible to someone outside the build in under a minute, via a case study and self-service integration guide, not just source code.

## Technical Approach

- **Voice layer**: ElevenLabs Conversational AI agent (`gemini-2.5-flash` as the underlying LLM, chosen for cost, not capability, this task doesn't need a larger model).
- **Tool layer**: one webhook tool, `look_up_order`, registered directly on the agent (`tool_ids`, not just present in the workspace's tool library, an easy thing to get wrong).
- **Backend**: FastAPI on Vercel, single POST endpoint, stateless.
- **Data layer**: Supabase Postgres. One `orders` table, 30 seed rows across 3 stores, RLS enabled with an explicit `GRANT` to `service_role` (RLS alone does not grant base table access, this was a real bug, not a design choice).
- **Multi-tenant design**: store is a required parameter on every lookup; one shared table and one shared tool serve three separate demo brands rather than three separate deployments.
- **Multi-language**: implemented via `language_presets` on the agent (German, Japanese, Korean, Chinese), each with a translated first message and correct language code. Translations were written without native-speaker review, flagged as a known gap, not verified as production-quality.
- **Demo surface**: a standalone widget page, deliberately designed around the subject (a dispatch-ticket visual language), showing real, working test values directly on the page rather than requiring a visitor to guess or dig for one.
- **Documentation**: a case study (architecture and real debugging narrative) and a self-service integration guide (how to build the same pattern elsewhere), both linked from the README, not just implied by the code.

## Explicit Non-Goals

- No order modification, cancellation, or refund handling.
- No real live carrier tracking integration yet (UPS/FedEx/USPS APIs). Scoped as a documented next step, not built.
- No real phone number (Twilio). The widget and ElevenLabs dashboard test call are the only access points; this was a deliberate cost decision, not a limitation encountered by accident.
- No dynamic-variable pre-call store selection (a dropdown that sets store before the conversation starts). Considered, not implemented, since the exact widget-side syntax wasn't verified and shipping an unconfirmed feature was judged worse than not shipping it.
- No functional handoff to a human on failed lookups, despite the agent saying it will.

## What changed from the original PRD

- Single store → three demo stores through one shared schema.
- English only → five languages.
- Mock JSON file → live Postgres database with real permissions and real bugs.
- No supporting documentation → case study and self-service guide, linked from the README.
- Plain widget page → redesigned around the subject matter, with real test data visible on load.

## Next

- Carrier API enrichment once an order ships, layering a real third-party integration on top of the owned database.
- Native-speaker review of the four translated first messages before treating multi-language as demo-ready for those audiences.
- Dynamic-variable store selection, once the widget's exact variable-injection syntax is confirmed rather than assumed.
