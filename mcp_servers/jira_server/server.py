"""Jira MCP server — exposes create_support_ticket tool via stdio."""

import base64
import os
import sys
from pathlib import Path

import httpx
from mcp.server.fastmcp import FastMCP

# Load .env from project root when spawned as subprocess
_project_root = Path(__file__).resolve().parents[2]
try:
    from dotenv import load_dotenv

    load_dotenv(_project_root / ".env", override=True)
except ImportError:
    pass

mcp = FastMCP("jira-support")


def _auth_header() -> str:
    email = os.environ.get("JIRA_EMAIL", "")
    token = os.environ.get("JIRA_API_TOKEN", "")
    if not email or not token:
        raise ValueError(
            "JIRA_EMAIL and JIRA_API_TOKEN must be set in .env"
        )
    creds = base64.b64encode(f"{email}:{token}".encode()).decode()
    return f"Basic {creds}"


def _text_to_adf(text: str) -> dict:
    paragraphs = []
    for line in text.splitlines():
        if line.strip():
            paragraphs.append(
                {
                    "type": "paragraph",
                    "content": [{"type": "text", "text": line}],
                }
            )
    if not paragraphs:
        paragraphs.append(
            {
                "type": "paragraph",
                "content": [{"type": "text", "text": text or "(no description)"}],
            }
        )
    return {"type": "doc", "version": 1, "content": paragraphs}


@mcp.tool()
def create_support_ticket(
    summary: str,
    description: str,
    priority: str = "Highest",
    issue_type: str | None = None,
    project_key: str | None = None,
    labels: str = "a2a-pilot,support",
) -> str:
    """Create a Jira support ticket.

    Args:
        summary: Short ticket title (e.g. 'P1 — User cannot login AUTH_401').
        description: Full incident details including user email, error/charge info, steps tried.
        priority: Jira priority name — use 'Highest' for P1, 'High' for P2.
        issue_type: Jira issue type (default from JIRA_ISSUE_TYPE env or 'Bug').
        project_key: Jira project key (default from JIRA_PROJECT_KEY env).
        labels: Comma-separated labels to attach.

    Returns:
        Created issue key and browse URL.
    """
    base_url = os.environ.get("JIRA_BASE_URL", "").rstrip("/")
    if not base_url:
        raise ValueError("JIRA_BASE_URL must be set in .env")

    project = project_key or os.environ.get("JIRA_PROJECT_KEY", "SUPPORT")
    issue = issue_type or os.environ.get("JIRA_ISSUE_TYPE", "Bug")
    label_list = [l.strip() for l in labels.split(",") if l.strip()]

    payload = {
        "fields": {
            "project": {"key": project},
            "summary": summary,
            "description": _text_to_adf(description),
            "issuetype": {"name": issue},
            "priority": {"name": priority},
            "labels": label_list,
        }
    }

    url = f"{base_url}/rest/api/3/issue"
    headers = {
        "Authorization": _auth_header(),
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    with httpx.Client(timeout=30.0) as client:
        response = client.post(url, json=payload, headers=headers)

    if response.status_code >= 400:
        return (
            f"Failed to create Jira ticket (HTTP {response.status_code}): "
            f"{response.text}"
        )

    data = response.json()
    key = data.get("key", "UNKNOWN")
    browse_url = f"{base_url}/browse/{key}"
    return f"Created Jira ticket {key}. URL: {browse_url}"


if __name__ == "__main__":
    mcp.run(transport="stdio")
