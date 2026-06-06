import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from google.adk.agents import Agent
from google.adk.agents.remote_a2a_agent import AGENT_CARD_WELL_KNOWN_PATH, RemoteA2aAgent

from shared.config import ADK_MODEL, BILLING_AGENT_URL, LOGIN_AGENT_URL

ROUTER_INSTRUCTION = """
You are the support router. You greet users and route them to the correct specialist via A2A.

ROUTING RULES — delegate to exactly ONE specialist per user message:
- login_specialist: login problems, cannot sign in, password issues, AUTH_401, session expired,
  account locked, 2FA, app crashes on login, authentication errors
- billing_specialist: charges, billing, refunds, subscriptions, unauthorized charges,
  duplicate payments, unrecognized charges on card, invoice disputes

WORKFLOW:
1. If the user's intent is unclear, ask ONE clarifying question (login or billing?).
2. Once intent is clear, delegate the FULL conversation to the appropriate specialist.
3. Do NOT try to solve login or billing issues yourself — always delegate.
4. Pass the user's message and context to the specialist. The specialist will use KB (RAG)
   and escalate to Jira if needed.
5. Relay the specialist's response back to the user clearly.

You are the front door — specialists own the conversation after routing.
"""

login_specialist = RemoteA2aAgent(
    name="login_specialist",
    description=(
        "Login/app authentication specialist. Skills: app-login, AUTH_401, session-error, "
        "password-reset, account-lockout, 2fa. Uses KB and can create Jira tickets."
    ),
    agent_card=f"{LOGIN_AGENT_URL.rstrip('/')}/{AGENT_CARD_WELL_KNOWN_PATH}",
)

billing_specialist = RemoteA2aAgent(
    name="billing_specialist",
    description=(
        "Billing and payments specialist. Skills: billing-dispute, unauthorized-charge, "
        "refund, subscription, duplicate-charge. Uses KB and can create Jira tickets."
    ),
    agent_card=f"{BILLING_AGENT_URL.rstrip('/')}/{AGENT_CARD_WELL_KNOWN_PATH}",
)

root_agent = Agent(
    model=ADK_MODEL,
    name="support_router",
    description=(
        "Routes user support requests to login or billing specialist agents via A2A protocol."
    ),
    instruction=ROUTER_INSTRUCTION,
    sub_agents=[login_specialist, billing_specialist],
)
