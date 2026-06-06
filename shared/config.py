import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env", override=True)

ADK_MODEL = os.getenv("ADK_MODEL", "gemini-2.0-flash")

LOGIN_AGENT_URL = os.getenv("LOGIN_AGENT_URL", "http://127.0.0.1:8001")
BILLING_AGENT_URL = os.getenv("BILLING_AGENT_URL", "http://127.0.0.1:8002")
TICKET_AGENT_URL = os.getenv("TICKET_AGENT_URL", "http://127.0.0.1:8003")

KB_ROOT = PROJECT_ROOT / "kb"

JIRA_MCP_SERVER = PROJECT_ROOT / "mcp_servers" / "jira_server" / "server.py"
