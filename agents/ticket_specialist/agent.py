import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from google.adk.agents import Agent
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

from shared.config import ADK_MODEL, JIRA_MCP_SERVER

TICKET_INSTRUCTION = """
You are a support ticket specialist. You receive escalated incidents from login or billing agents.

WORKFLOW:
1. Parse the handoff: incident type, user details, priority (P1 or P2), chat summary.
2. Build a Jira ticket:
   - summary: "[P1] Login — AUTH_401 session expired" or "[P1] Billing — $50 unauthorized charge"
   - description: structured sections:
     * Category (Login / Billing)
     * User email
     * Issue details (error message OR charge amount/date/card)
     * Device/app version (login) or charge descriptor (billing)
     * Steps already tried
     * KB article referenced
     * Chat summary
3. You MUST call the create_support_ticket MCP tool (exact name — no other ticket tool exists):
   - priority: "Highest" for P1, "High" for P2
   - labels: include incident type e.g. "login" or "billing"
4. Return the ticket key and URL to the calling agent.

Do not ask the user questions — you only create tickets from structured handoffs.
"""

_python = sys.executable
_jira_server = str(JIRA_MCP_SERVER.resolve())

jira_mcp = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command=_python,
            args=[_jira_server],
            env=os.environ.copy(),
        ),
    ),
    tool_filter=["create_support_ticket"],
)

root_agent = Agent(
    model=ADK_MODEL,
    name="ticket_specialist",
    description=(
        "Creates Jira support tickets from structured incident handoffs using MCP."
    ),
    instruction=TICKET_INSTRUCTION,
    tools=[jira_mcp],
)

a2a_app = to_a2a(root_agent, port=8003)
