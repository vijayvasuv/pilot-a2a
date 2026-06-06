"""ADK function tools shared by specialist agents."""

from google.adk.tools.tool_context import ToolContext

from shared.rag import format_kb_results, search_kb


def search_login_kb(query: str) -> str:
    """Search the login/app support knowledge base for troubleshooting guidance.

    Args:
        query: The user's issue, error message, or symptom to look up.

    Returns:
        Relevant KB articles with troubleshooting steps.
    """
    results = search_kb(query, agent_type="login", top_k=3)
    return format_kb_results(results)


def search_billing_kb(query: str) -> str:
    """Search the billing support knowledge base for dispute and charge guidance.

    Args:
        query: The billing issue, charge description, or symptom to look up.

    Returns:
        Relevant KB articles with resolution steps.
    """
    results = search_kb(query, agent_type="billing", top_k=3)
    return format_kb_results(results)


def escalate_login_incident(
    user_email: str,
    error_message: str,
    app_version: str,
    device: str,
    steps_tried: str,
    priority: str,
    chat_summary: str,
    tool_context: ToolContext,
    kb_article_used: str = "",
) -> str:
    """Escalate an unresolved login incident to Jira via ticket_specialist.

    Call this when KB troubleshooting failed OR the user asks to escalate/create a ticket.
    Do NOT call create_ticket or create_support_ticket — use this tool only.

    Args:
        user_email: User's account email.
        error_message: Error shown on screen (e.g. AUTH_401 session expired).
        app_version: App version number.
        device: Device/OS info (e.g. Android 14).
        steps_tried: Comma-separated steps already attempted.
        priority: P1 or P2.
        chat_summary: Brief summary of the conversation.
        kb_article_used: KB article referenced, if any.

    Returns:
        Confirmation that escalation was initiated.
    """
    tool_context.actions.transfer_to_agent = "ticket_specialist"
    return f"""LOGIN INCIDENT HANDOFF — create Jira ticket
type: login_incident
priority: {priority}
user_email: {user_email}
error_message: {error_message}
app_version: {app_version}
device: {device}
steps_tried: {steps_tried}
kb_article_used: {kb_article_used or "session-expired"}
chat_summary: {chat_summary}"""


def escalate_billing_incident(
    user_email: str,
    charge_amount: str,
    charge_date: str,
    card_last_four: str,
    charge_description: str,
    steps_tried: str,
    priority: str,
    chat_summary: str,
    tool_context: ToolContext,
    kb_article_used: str = "",
) -> str:
    """Escalate an unresolved billing incident to Jira via ticket_specialist.

    Call this for billing escalations or when user requests a ticket.
    Do NOT call create_ticket or create_support_ticket — use this tool only.

    Args:
        user_email: User's account email.
        charge_amount: Charge amount with currency.
        charge_date: Date of charge.
        card_last_four: Last 4 digits of card.
        charge_description: Statement descriptor or charge details.
        steps_tried: Comma-separated steps already attempted.
        priority: P1 or P2.
        chat_summary: Brief summary of the conversation.
        kb_article_used: KB article referenced, if any.

    Returns:
        Confirmation that escalation was initiated.
    """
    tool_context.actions.transfer_to_agent = "ticket_specialist"
    return f"""BILLING INCIDENT HANDOFF — create Jira ticket
type: billing_incident
priority: {priority}
user_email: {user_email}
charge_amount: {charge_amount}
charge_date: {charge_date}
card_last_four: {card_last_four}
charge_description: {charge_description}
steps_tried: {steps_tried}
kb_article_used: {kb_article_used}
chat_summary: {chat_summary}"""
