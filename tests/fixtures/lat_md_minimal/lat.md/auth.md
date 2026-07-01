Authentication domain: handles login, sessions, and OAuth token exchange.

## OAuth Flow

Third-party login exchanges a code for a token. See [[src/auth.ts#validateToken]] for the
validation entrypoint. Relates to [[billing#Plan Limits]] for gating premium-only providers.

## Session Refresh

Refreshes short-lived session tokens without re-prompting the user.
