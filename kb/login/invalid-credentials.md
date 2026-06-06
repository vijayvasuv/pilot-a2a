# Invalid Credentials

## Symptoms
- "Invalid email or password" on login screen
- User is certain password is correct
- Recently changed password but old password still "works" on web

## Quick fixes
1. Confirm email has no trailing spaces; try lowercase
2. Use "Forgot password" flow — wait 5 minutes for reset email
3. Check spam folder for reset link
4. If using SSO (Google/Apple), try that login method instead

## Common causes
- Caps Lock enabled
- Password changed on web but mobile app cached old session
- Account not yet verified after signup

## When to escalate
- Password reset emails never arrive (after 15 min)
- SSO login also fails
- User sees "account locked" after 5+ failed attempts

## Priority
- P1 if account locked and user cannot access paid features
- P2 for first-time login confusion
