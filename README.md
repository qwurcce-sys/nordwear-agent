# NordWear Support Agent

A customer-support AI agent for **NordWear**, a fictional Nordic clothing
brand. It answers shipping / returns / sizing questions from a fixed policy
set, looks up order status, captures leads it can't answer, and escalates
sensitive issues to a human.

Built as a portfolio demo: Python + the Anthropic SDK used directly (no
LangChain), with a hand-written tool-use loop so the agent's decision-making
is fully transparent.

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # then add your real ANTHROPIC_API_KEY
python agent.py
```

`.env` is gitignored — your API key is never committed.

## How it works

- **`agent.py`** — the agent loop. Each user turn calls the Messages API; if
  the model asks for a tool (`stop_reason == "tool_use"`), the loop runs it,
  feeds the result back, and calls the model again. It repeats until the model
  returns a normal answer (`stop_reason == "end_turn"`).
- **`tools.py`** — the four tools and the canonical store content. The store
  policies live here once and are both (a) searched by the knowledge-base tool
  and (b) rendered into the system prompt, so there is a single source of truth.

## Tools

| Tool | Purpose |
|------|---------|
| `search_knowledge_base(query)` | Find shipping / returns / FAQ policy text. |
| `get_order_status(order_id)` | Look up a demo order (e.g. `NW-1001`). |
| `capture_lead(name, email, question)` | Record questions the bot can't answer. |
| `escalate_to_human(reason)` | Hand off complaints / sensitive issues. |

## Guardrails

The system prompt restricts the agent to the provided policies: it must never
invent shipping times or prices, must call `get_order_status` for any order
question, and must capture a lead or escalate when it can't answer confidently.

## Model

Uses `claude-sonnet-4-6`. Change `MODEL` at the top of `agent.py` to swap it.

## Next steps

- Wire `capture_lead` to Google Sheets (currently logs only).
- Wire `escalate_to_human` to a ticketing system / team notification.
- Replace the in-file policies and fake order book with real data sources.
- Add a web front-end (the current entry point is a terminal REPL).
