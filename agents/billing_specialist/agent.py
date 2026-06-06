import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from google.adk.agents import Agent
from google.adk.agents.remote_a2a_agent import AGENT_CARD_WELL_KNOWN_PATH, RemoteA2aAgent
from google.adk.a2a.utils.agent_to_a2a import to_a2a

from shared.config import ADK_MODEL, TICKET_AGENT_URL
from shared.tools import escalate_billing_incident, search_billing_kb

BILLING_INSTRUCTION = """
You are a billing and payments support specialist.

TOOLS YOU HAVE:
- search_billing_kb: look up billing/dispute guidance
- escalate_billing_incident: hand off to ticket_specialist for Jira ticket creation

YOU DO NOT HAVE create_ticket, create_support_ticket, or any direct Jira tools.

WORKFLOW:
1. ALWAYS call search_billing_kb first when the user reports a billing issue.
2. Suggest KB resolution steps BEFORE collecting personal details (check payment history,
   email receipt, statement descriptor). Wait for user to confirm charge is still unrecognized.
3. Only then collect details ONE at a time:
   - Charge amount and currency
   - Date of charge
   - Last 4 digits of card (never ask for full card number)
   - User email on account
4. ESCALATE with escalate_billing_incident (P1) if:
   - Unauthorized charge over $50
   - Suspected fraud
   - Multiple duplicate charges in 24 hours
5. Otherwise, if user is still unresolved OR requests a ticket, call escalate_billing_incident
   with all collected details. priority: P1 for fraud/large charges; P2 otherwise.
6. Tell the user the Jira ticket ID when ticket_specialist confirms creation.

Never ask for full card numbers or CVV. Be empathetic and precise.
"""

ticket_specialist = RemoteA2aAgent(
    name="ticket_specialist",
    description=(
        "Creates P1/P2 Jira support tickets via MCP. Delegate here for billing "
        "escalations and unresolved disputes."
    ),
    agent_card=f"{TICKET_AGENT_URL.rstrip('/')}/{AGENT_CARD_WELL_KNOWN_PATH}",
)

root_agent = Agent(
    model=ADK_MODEL,
    name="billing_specialist",
    description=(
        "Handles billing disputes: unrecognized charges, duplicate subscriptions, "
        "and refund requests."
    ),
    instruction=BILLING_INSTRUCTION,
    tools=[search_billing_kb, escalate_billing_incident],
    sub_agents=[ticket_specialist],
)

a2a_app = to_a2a(root_agent, port=8002)
