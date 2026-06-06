# P1 vs P2 Escalation Criteria

## Create P1 (Highest priority) when ANY of these apply

### Login
- Complete account lockout with active paid subscription
- AUTH_401 or auth errors persist after all KB troubleshooting steps
- SSO and password reset both fail
- Security concern: suspected account takeover

### Billing
- Unauthorized charge over $50
- Multiple duplicate charges in 24 hours
- User reports fraud / card compromised
- Charged after confirmed cancellation before trial end

## Create P2 (High priority) when
- Issue unresolved but user has partial workaround
- First-time user confusion (not lockout)
- Refund request within policy window
- Charges under $50 with unclear but non-fraudulent origin

## Ticket must include
- User email
- Issue category (login / billing)
- Error message or charge details
- Device/app version (login) or card last 4 + amount + date (billing)
- Steps already tried from KB
- Chat summary
