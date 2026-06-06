# Session Expired (AUTH_401)

## Symptoms
- Error on screen: `AUTH_401 — session expired`
- User was previously logged in but gets kicked out
- Happens after app update or long idle time

## Quick fixes (try in order)
1. Force-close the app and reopen
2. Clear app cache: Settings → Apps → [App Name] → Clear Cache (do NOT clear data unless instructed)
3. Log out completely, then log back in
4. Check device date/time is set automatically

## When to escalate
- User still sees AUTH_401 after cache clear and re-login
- Error persists across Wi-Fi and mobile data
- Affects multiple devices with same account

## Priority
- P1 if user cannot access account at all and has active subscription
- P2 if intermittent and workaround exists
