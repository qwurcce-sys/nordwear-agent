"""Tool implementations for the NordWear customer-support agent.

Everything here is a stub for a portfolio demo:
- `search_knowledge_base` reads from the in-file STORE_POLICIES (single source
  of truth, also rendered into the system prompt by agent.py).
- `get_order_status` returns canned data for a few fake orders.
- `capture_lead` / `escalate_to_human` just log; wire real backends later.

Each tool has two parts: a JSON-schema definition the model sees (in TOOLS),
and a Python function that actually runs (dispatched via `dispatch_tool`).
"""

import json
import logging

logger = logging.getLogger("nordwear.tools")


# --- Canonical store content -------------------------------------------------
# The agent must answer ONLY from this. Numbers/prices live here so the model
# never has to invent them.
STORE_POLICIES = {
    "shipping": (
        "Standard shipping is 3-5 business days and free on orders over $75 "
        "(otherwise a flat $6). Express shipping is 1-2 business days for $15. "
        "We ship to the US, EU, and the Nordic countries. Orders placed before "
        "2pm CET ship the same business day."
    ),
    "returns": (
        "Returns are accepted within 30 days of delivery. Items must be unworn "
        "with original tags attached. Returns are free using the prepaid label "
        "in your confirmation email. Refunds are issued to the original payment "
        "method within 5-7 business days of us receiving the item."
    ),
    "faq": (
        "Our garments run true to size; see the size guide on each product "
        "page. Most knitwear is 100% merino wool and machine washable on cold, "
        "flat dry. You can change or cancel an order within 1 hour of placing "
        "it by replying to your confirmation email."
    ),
}


# --- Fake order book ---------------------------------------------------------
FAKE_ORDERS = {
    "NW-1001": {
        "order_id": "NW-1001",
        "status": "shipped",
        "items": ["Fjord Merino Sweater (M, Slate)"],
        "carrier": "PostNord",
        "tracking": "PN123456789SE",
        "estimated_delivery": "2026-07-02",
    },
    "NW-1002": {
        "order_id": "NW-1002",
        "status": "processing",
        "items": ["Aurora Wool Beanie (Rust)", "Tundra Scarf (Charcoal)"],
        "carrier": None,
        "tracking": None,
        "estimated_delivery": "2026-07-05",
    },
    "NW-1003": {
        "order_id": "NW-1003",
        "status": "delivered",
        "items": ["Glacier Base Layer (L, Black)"],
        "carrier": "DHL",
        "tracking": "DHL987654321",
        "estimated_delivery": "2026-06-20",
    },
}


# --- Tool functions ----------------------------------------------------------
def search_knowledge_base(query: str) -> str:
    """Return store-policy sections relevant to the query (keyword match stub)."""
    q = query.lower()
    terms = [w for w in q.split() if len(w) > 3]
    hits = []
    for topic, text in STORE_POLICIES.items():
        if topic in q or any(term in text.lower() for term in terms):
            hits.append(f"[{topic.upper()}]\n{text}")
    logger.info("search_knowledge_base(query=%r) -> %d section(s)", query, len(hits))
    if not hits:
        return (
            "No matching policy found. Do not guess — if the customer still "
            "needs an answer, capture a lead or escalate to a human."
        )
    return "\n\n".join(hits)


def get_order_status(order_id: str) -> str:
    """Look up a single order by ID. Returns JSON, or a not-found message."""
    order = FAKE_ORDERS.get(order_id.strip().upper())
    logger.info(
        "get_order_status(order_id=%r) -> %s", order_id, "found" if order else "not found"
    )
    if order is None:
        known = ", ".join(FAKE_ORDERS)
        return f"No order found with ID {order_id!r}. Known demo orders: {known}."
    return json.dumps(order, indent=2)


def capture_lead(name: str, email: str, question: str) -> str:
    """Record a lead we couldn't answer confidently. TODO: write to Google Sheets."""
    logger.info("capture_lead | name=%s | email=%s | question=%s", name, email, question)
    return f"Lead captured for {name} ({email}). The team will follow up by email."


def escalate_to_human(reason: str) -> str:
    """Hand the conversation to a human. TODO: open a ticket / ping the team."""
    logger.warning("escalate_to_human | reason=%s", reason)
    return "Escalated to a human agent. A team member will take over shortly."


# --- Schemas the model sees --------------------------------------------------
TOOLS = [
    {
        "name": "search_knowledge_base",
        "description": (
            "Search NordWear's store policies (shipping, returns, FAQ) for the "
            "information needed to answer a customer question. Call this before "
            "answering any policy, shipping, returns, sizing, or care question."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "What to look up, e.g. 'return window' or 'express shipping cost'.",
                }
            },
            "required": ["query"],
        },
    },
    {
        "name": "get_order_status",
        "description": (
            "Look up the status of a specific customer order by its ID "
            "(format NW-XXXX). Always use this for any question about a "
            "particular order — never guess an order's status."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "order_id": {
                    "type": "string",
                    "description": "The order ID, e.g. 'NW-1001'.",
                }
            },
            "required": ["order_id"],
        },
    },
    {
        "name": "capture_lead",
        "description": (
            "Record a customer's contact details and question when you cannot "
            "answer confidently from the knowledge base, so the team can follow "
            "up. Ask the customer for their name and email first if you don't "
            "have them."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Customer's name."},
                "email": {"type": "string", "description": "Customer's email address."},
                "question": {
                    "type": "string",
                    "description": "The question or request to follow up on.",
                },
            },
            "required": ["name", "email", "question"],
        },
    },
    {
        "name": "escalate_to_human",
        "description": (
            "Escalate to a human agent for issues the bot should not handle "
            "alone (complaints, refunds disputes, anything sensitive or urgent)."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "reason": {
                    "type": "string",
                    "description": "Why this needs a human.",
                }
            },
            "required": ["reason"],
        },
    },
]


_TOOL_FUNCTIONS = {
    "search_knowledge_base": search_knowledge_base,
    "get_order_status": get_order_status,
    "capture_lead": capture_lead,
    "escalate_to_human": escalate_to_human,
}


def dispatch_tool(name: str, tool_input: dict) -> str:
    """Run a tool by name with the model-provided input, returning a string."""
    func = _TOOL_FUNCTIONS.get(name)
    if func is None:
        return f"Error: unknown tool {name!r}."
    try:
        return func(**tool_input)
    except TypeError as exc:
        return f"Error calling {name}: {exc}"


def render_policies() -> str:
    """Render the store policies as markdown for embedding in the system prompt."""
    return "\n\n".join(
        f"## {topic.title()}\n{text}" for topic, text in STORE_POLICIES.items()
    )
