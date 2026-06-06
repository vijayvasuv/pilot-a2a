import os
import sys

# Ensure project root is on path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from google.adk.agents import Agent
from google.adk.agents.remote_a2a_agent import AGENT_CARD_WELL_KNOWN_PATH, RemoteA2aAgent
from google.adk.a2a.utils.agent_to_a2a import to_a2a

from shared.config import ADK_MODEL, TICKET_AGENT_URL
from shared.tools import escalate_login_incident, search_login_kb

LOGIN_INSTRUCTION = """
You are a login and app authentication support specialist.

TOOLS YOU HAVE:
- search_login_kb: look up troubleshooting steps
- escalate_login_incident: hand off to ticket_specialist for Jira ticket creation

YOU DO NOT HAVE create_ticket, create_support_ticket, or any direct Jira tools.

WORKFLOW:
1. ALWAYS call search_login_kb first when the user reports an error (e.g. AUTH_401).
2. Suggest KB troubleshooting steps BEFORE asking for email or personal details.
   Wait for the user to confirm whether the workaround worked.
3. Only if workarounds fail, collect details ONE at a time:
   - Email used for the account
   - App version and device (e.g. Android 14, iOS 17)
   - What they already tried from the KB steps
4. If the user is still blocked OR explicitly asks to escalate/create a ticket:
   - Call escalate_login_incident with all collected details
   - priority: P1 if complete lockout or AUTH_401 persists after fixes; else P2
   - NEVER invent a different tool name for ticket creation
5. After escalation, tell the user the Jira ticket ID when ticket_specialist confirms creation.

Be empathetic, concise, and do not invent fixes not supported by the KB.
"""

ticket_specialist = RemoteA2aAgent(
    name="ticket_specialist",
    description=(
        "Creates P1/P2 Jira support tickets via MCP. Delegate here when login "
        "issue is unresolved or user requests escalation."
    ),
    agent_card=f"{TICKET_AGENT_URL.rstrip('/')}/{AGENT_CARD_WELL_KNOWN_PATH}",
)

root_agent = Agent(
    model=ADK_MODEL,
    name="login_specialist",
    description=(
        "Handles app login issues: invalid credentials, session expired (AUTH_401), "
        "account lockout, and 2FA problems."
    ),
    instruction=LOGIN_INSTRUCTION,
    tools=[search_login_kb, escalate_login_incident],
    sub_agents=[ticket_specialist],
)

a2a_app = to_a2a(root_agent, port=8001)
