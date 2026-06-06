# Account Locked / 2FA Issues

## Symptoms
- "Account temporarily locked due to too many attempts"
- 2FA code not accepted
- Authenticator app codes out of sync

## Quick fixes
1. Wait 30 minutes before retrying (auto-unlock)
2. For 2FA: sync device time to network time
3. Use backup codes if available (Settings → Security → Backup codes)
4. Try SMS 2FA if authenticator fails

## When to escalate
- Lockout exceeds 30 minutes
- User has no backup codes and lost authenticator device
- 2FA codes consistently rejected with correct time sync

## Priority
- P1 if user is locked out of paid account with time-sensitive access
- P2 if user can still access via web but not mobile
