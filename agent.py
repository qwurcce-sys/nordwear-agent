"""NordWear customer-support agent — a manual Anthropic tool-use loop.

This file is deliberately written without the SDK's tool runner so the
agentic loop is fully visible: you can see exactly where the model decides
to call a tool versus give a final answer.

Run it:
    python agent.py
"""

import logging
import os
import sys

import anthropic
from dotenv import load_dotenv

from tools import TOOLS, dispatch_tool, render_policies

# Load ANTHROPIC_API_KEY (and anything else) from .env into the environment.
load_dotenv()

# One simple log line per message — the tools log here too.
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("nordwear.agent")

MODEL = "claude-sonnet-4-6"
MAX_TOKENS = 1024
MAX_STEPS = 6  # safety cap on tool round-trips within a single turn


# The store policies are rendered straight from tools.py so there is exactly
# one source of truth. The rules tell the model how to behave; the policies
# give it the facts it is allowed to use.
SYSTEM_PROMPT = f"""You are the customer-support assistant for NordWear, a \
Nordic clothing brand. You are friendly, concise, and accurate.

Rules you must always follow:
1. Answer ONLY from the store policies below and from tool results. If the \
answer is not there, say you are not sure — never invent shipping times, \
prices, dates, or policies.
2. For any question about a specific order, you MUST call get_order_status \
with the order ID. Never guess an order's status, tracking, or delivery date.
3. Before answering a shipping, returns, sizing, or care question, call \
search_knowledge_base to ground your answer.
4. If you cannot answer confidently from the policies or tools, use \
capture_lead to collect the customer's name, email, and question so the team \
can follow up. Use escalate_to_human for complaints, refund disputes, or \
anything sensitive or urgent.

Store policies (the only facts you may rely on):

{render_policies()}
"""


def _make_client() -> anthropic.Anthropic:
    """Build the client, failing early with a clear message if the key is missing."""
    if not os.environ.get("ANTHROPIC_API_KEY"):
        sys.exit(
            "ANTHROPIC_API_KEY is not set. Copy .env.example to .env and add "
            "your key, or export it in your shell."
        )
    # The SDK reads ANTHROPIC_API_KEY from the environment automatically.
    return anthropic.Anthropic()


client = _make_client()


def run_turn(messages: list[dict]) -> str:
    """Run one user turn to completion, executing tools until the model is done.

    `messages` is the full running conversation; this function appends the
    assistant (and any tool_result) messages to it in place, and returns the
    final assistant text to show the user.
    """
    for _ in range(MAX_STEPS):
        response = client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            system=[
                {
                    "type": "text",
                    "text": SYSTEM_PROMPT,
                    "cache_control": {"type": "ephemeral"},
                }
            ],
            tools=TOOLS,
            messages=messages,
        )

        # Preserve the assistant's content verbatim — it may contain tool_use
        # blocks that must be echoed back alongside their tool_result blocks.
        messages.append({"role": "assistant", "content": response.content})

        # No tool requested -> this is the final answer for this turn.
        if response.stop_reason != "tool_use":
            return _text_of(response.content)

        # Otherwise: run every tool the model asked for, collect the results,
        # and feed them back as a single user message so the loop can continue.
        tool_results = []
        for block in response.content:
            if block.type != "tool_use":
                continue
            logger.info("-> tool: %s(%s)", block.name, block.input)
            result = dispatch_tool(block.name, block.input)
            tool_results.append(
                {
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": result,
                }
            )
        messages.append({"role": "user", "content": tool_results})

    return (
        "Sorry — I got stuck working on that. Let me hand you to a human "
        "teammate who can help."
    )


def _text_of(content: list) -> str:
    """Join the text blocks of an assistant response into a single string."""
    return "\n".join(block.text for block in content if block.type == "text").strip()


def main() -> None:
    print("NordWear support agent. Type 'quit' to exit.\n")
    messages: list[dict] = []
    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if user_input.lower() in {"quit", "exit"}:
            break
        if not user_input:
            continue
        messages.append({"role": "user", "content": user_input})
        reply = run_turn(messages)
        print(f"\nNordWear: {reply}\n")


if __name__ == "__main__":
    main()
