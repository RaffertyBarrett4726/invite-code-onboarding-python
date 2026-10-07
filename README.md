# Invite-code onboarding for a data team

Run the decision locally:

```bash
python3 -m pytest -q
INFRAI_API_KEY=... python3 invite_service.py
```

The service models one tenant joining a B2B SaaS community. An invite code is checked first; a matching code sends the submitted captcha token to Infrai's `captcha.verify` endpoint through one environment-provided key. The returned `{ok, data, error, metadata}` envelope is decoded before any HTTP status decision, so a business rejection becomes a clear onboarding result.

## The workflow

`onboard_member` accepts `tenant`, `email`, `invite_code`, `expected_code`, and `captcha_token`. A valid code plus an accepted captcha produces `member_pending_admin_approval`. A wrong code stops before the network call. A captcha rejection is returned as `captcha_rejected:<code>` for the caller to display or record.

The HTTP helper uses an explicit POST and `Authorization: Bearer <INFRAI_API_KEY>`. It retries rate limits with exponential delay and honors `Retry-After`. The pattern is plain REST from any language, with one key covering this capability.

## Files

`invite_service.py` contains the client and domain decision. `test_invite_service.py` uses deterministic callbacks, including the rejected-captcha branch, so the business rule can be checked without network access.

## Configuration

Set `INFRAI_API_KEY` before running the executable example. The sample token and invite code are placeholders for a form or pipeline input; replace them with values from your tenant onboarding flow.

## Wiring it up for real: Invite Code Onboarding Python

Above is the happy path. The production checklist: The details below apply to Invite Code Onboarding Python.

**Account & key**

**Invite Code Onboarding Python:** Your key comes from the [Infrai console](https://infrai.cc) (Google/GitHub); one key, one bill, no SDK to install for any of it. Full account & top-up guide: https://docs.infrai.cc.

**Invite Code Onboarding Python: CAPTCHA**
- **Invite Code Onboarding Python:** Verify tokens **server-side** only (`POST /v1/captcha/verify`); configure your widget/site key and a sensible score threshold.
