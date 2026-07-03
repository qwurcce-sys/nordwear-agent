# NordWear Support Agent

An AI customer-support agent for Shopify stores. It answers shipping, returns, and FAQ questions instantly, looks up order status on demand, and captures a lead whenever it can't answer confidently — so no customer is left waiting and no sale is lost to a slow reply.

> **Demo project.** Built around a fictional store ("NordWear") to showcase the architecture. The knowledge base, tools, and integrations are designed to be swapped per client with minimal changes.

---

## The problem it solves

Small Shopify stores get the same questions dozens of times a day — *"Where's my order?"*, *"What's your return policy?"*, *"Do you ship to my country?"*. Answering them manually is slow, happens only during working hours, and every unanswered message is a customer who may not come back.

This agent handles that first line of support automatically, 24/7, and hands off cleanly to a human when needed.

## What it does

| Capability | Description |
|---|---|
| **Answers policy questions** | Responds to shipping, returns, sizing, and care questions grounded in the store's own policies |
| **Checks order status** | Looks up a specific order by ID and reports status, tracking, and delivery estimate |
| **Captures leads** | When it can't answer confidently, it collects the customer's name, email, and question for team follow-up |
| **Escalates to a human** | Routes complaints, refund disputes, and sensitive issues to a human agent instead of guessing |

## Key design principle: no hallucinated answers

The agent answers **only** from the store's policies and live tool results. It never invents shipping times, prices, or delivery dates. If the information isn't available, it captures a lead or escalates — it does not guess. This is what makes it safe to put in front of real customers.

## How it works

The
cat > ~/Documents/nordwear-agent/README.md << 'EOF'
# NordWear Support Agent

An AI customer-support agent for Shopify stores. It answers shipping, returns, and FAQ questions instantly, looks up order status on demand, and captures a lead whenever it can't answer confidently — so no customer is left waiting and no sale is lost to a slow reply.

> **Demo project.** Built around a fictional store ("NordWear") to showcase the architecture. The knowledge base, tools, and integrations are designed to be swapped per client with minimal changes.

---

## The problem it solves

Small Shopify stores get the same questions dozens of times a day — *"Where's my order?"*, *"What's your return policy?"*, *"Do you ship to my country?"*. Answering them manually is slow, happens only during working hours, and every unanswered message is a customer who may not come back.

This agent handles that first line of support automatically, 24/7, and hands off cleanly to a human when needed.

## What it does

| Capability | Description |
|---|---|
| **Answers policy questions** | Responds to shipping, returns, sizing, and care questions grounded in the store's own policies |
| **Checks order status** | Looks up a specific order by ID and reports status, tracking, and delivery estimate |
| **Captures leads** | When it can't answer confidently, it collects the customer's name, email, and question for team follow-up |
| **Escalates to a human** | Routes complaints, refund disputes, and sensitive issues to a human agent instead of guessing |

## Key design principle: no hallucinated answers

The agent answers **only** from the store's policies and live tool results. It never invents shipping times, prices, or delivery dates. If the information isn't available, it captures a lead or escalates — it does not guess. This is what makes it safe to put in front of real customers.

## How it works

The agent runs a transparent tool-use loop rather than a black-box framework, so its decision-making is fully visible:

1. The customer's message goes to the model along with the available tools.
2. The model decides whether it needs a tool (e.g. look up an order) or can answer directly.
3. If a tool is needed, the code runs it and returns the result to the model.
4. The loop repeats until the model has enough information to give a final answer.

A safety cap limits tool round-trips per turn, and the agent hands off to a human if it can't resolve a request.

## Tech stack

- **Python** — core agent and tools
- **Anthropic API (Claude)** — reasoning and tool use
- **Model-agnostic design** — the model is set in one place and can be swapped to fit a client's existing stack

## Project structure

| File | Purpose |
|---|---|
| \`agent.py\` | The agent loop — orchestrates the conversation and tool calls |
| \`tools.py\` | Tool definitions and implementations (knowledge base, order lookup, lead capture, escalation) |
| \`.env.example\` | Template for the API key (real keys are never committed) |
| \`requirements.txt\` | Python dependencies |

## Running it locally

\`\`\`bash
pip install -r requirements.txt
cp .env.example .env        # then add your Anthropic API key to .env
python agent.py
\`\`\`

## Adapting it for a store

The demo is built to be productized. For a real client, the main changes are: replace the store policies with the client's own, connect \`get_order_status\` to their Shopify order data, and wire \`capture_lead\` to their CRM or a spreadsheet.

---

*Built by Grigoriy Kirilin — custom AI agents for e-commerce support and lead capture.*
