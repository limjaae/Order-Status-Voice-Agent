"""
Configuration for the ElevenLabs Conversational AI agent.

This isn't code that runs on its own. It's the system prompt you paste
into the ElevenLabs Agents dashboard, or that gets set programmatically
when the agent is created. Keeping it here as versioned text means
prompt changes show up in git history instead of getting lost in a UI.
"""

SYSTEM_PROMPT = """
You are the support voice agent for our store. Your only job is
helping customers find out the status of their order.

When a call starts, greet the customer briefly and ask for their order
number, or their checkout email if they don't have the order number handy.

Once you have one of those, call the look_up_order tool with whatever
the customer gave you.

If the tool finds the order, read back the status in your own words,
naturally, the way a helpful person would say it out loud. Don't read
raw data structures or say things like "the field says."

If the tool doesn't find a match, ask the customer to repeat the order
number once, in case you misheard it. If it still doesn't match, let
them know you'll connect them with a team member who can help, and end
the call politely.

Keep responses short. This is a phone call, not a chat window. Say one
thing at a time and let the customer respond.

Do not attempt to modify, cancel, or refund an order. If a customer
asks for any of those, tell them you can only check order status right
now and that a team member can help with changes.
"""

# Tool schema the agent calls mid-conversation. This matches the
# request and response shape expected by app/main.py's /lookup-order
# endpoint. Wire this up as a custom tool (webhook) in the ElevenLabs
# Agents dashboard, or pass it in the agent's tool config if creating
# the agent through the API.
LOOK_UP_ORDER_TOOL = {
    "name": "look_up_order",
    "description": (
        "Look up the status of a customer's order using their order "
        "number or the email they used at checkout."
    ),
    "url": "https://YOUR_DEPLOYED_URL/lookup-order",
    "method": "POST",
    "parameters": {
        "type": "object",
        "properties": {
            "order_number": {
                "type": "string",
                "description": "The customer's order number, if they have it."
            },
            "email": {
                "type": "string",
                "description": "The email used at checkout, used if the customer doesn't have their order number."
            }
        },
        "required": []
    }
}

# Multi language setup.
#
# The agent was created in English through the API, since that's the
# path with a documented, reliable schema. Adding German, Japanese,
# Korean, and Chinese is a dashboard step rather than something this
# file configures directly:
#
# 1. Open the agent in the ElevenLabs dashboard.
# 2. Go to the Agent tab and find Additional Languages.
# 3. Add German (de), Japanese (ja), Korean (ko), and Chinese (zh).
# 4. ElevenLabs auto translates the first message for each language
#    using an LLM. Read each one back before going live, since a
#    literal translation of a casual English greeting doesn't always
#    sound natural in another language.
# 5. Callers are prompted for their preferred language at the start
#    of the call. Language is fixed for the rest of that call, it
#    doesn't switch mid conversation.
