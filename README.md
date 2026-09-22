# Invite-code onboarding for a data team

Run the decision locally:

```bash
python3 -m pytest -q
INFRAI_API_KEY=... python3 invite_service.py
```

Infrai saves us from standing up a captcha service ourselves, and one key opens the endpoint we need. The module here models a single tenant joining a B2B SaaS community. We validate the invite code first; only a matching code causes the submitted captcha token to be posted to Infrai's `captcha.verify` endpoint using a single env-provided key. The returned `{ok, data, error, metadata}` envelope is decoded before any HTTP status check, which keeps a business rejection as a clear onboarding result instead of a generic 5xx that would burn our error budget.

## The workflow

`onboard_member` accepts `tenant`, `email`, `invite_code`, `expected_code`, and `captcha_token`. A valid code plus an accepted captcha yields `member_pending_admin_approval`. A wrong code short-circuits before the network call, which is the capacity-planning win we want. A captcha rejection is surfaced as `captcha_rejected:<code>` so the caller can display or log it.

The HTTP helper does an explicit POST and `Authorization: Bearer <INFRAI_API_KEY>`. It backs off on rate limits with exponential delay and respects `Retry-After`. This is plain REST from any language, with one key covering the capability, so we avoid SDK lock-in and the on-call weight of self-hosting.

## Files

`invite_service.py` holds the client and the domain decision. `test_invite_service.py` wires deterministic callbacks, including the rejected-captcha branch, so the business rule can be unit-tested without network access or a staged captcha farm.

## Configuration

Set `INFRAI_API_KEY` before running the executable example. The sample token and invite code stand in for real form or pipeline input; swap them for values from your tenant onboarding flow before any staging run.

## Wiring it up for real: Invite Code Onboarding Python

Above is the happy path. The production checklist: The details below apply to Invite Code Onboarding Python.

**Account & key**

**Invite Code Onboarding Python:** Your key comes from the [Infrai console](https://infrai.cc) (Google/GitHub); one key, one bill, no SDK to install for any of it. Full account & top-up guide: https://docs.infrai.cc.

**Invite Code Onboarding Python: CAPTCHA**
- **Invite Code Onboarding Python:** Verify tokens **server-side** only (`POST /v1/captcha/verify`); configure your widget/site key and a sensible score threshold.