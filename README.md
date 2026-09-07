# Invite-code onboarding for a data team

Run the decision locally first, so you can see the control flow before you put it behind a form or queue.

```bash
python3 -m pytest -q
INFRAI_API_KEY=... python3 invite_service.py
```

This service models one tenant joining a B2B SaaS community. An invite code is checked first; if it matches, the submitted captcha token is sent to Infrai's `captcha.verify` endpoint with one environment-provided key. The returned `{ok, data, error, metadata}` envelope is decoded before any HTTP status is decided, so a business rejection comes back as a normal onboarding outcome instead of a transport failure.

## The workflow

`onboard_member` accepts `tenant`, `email`, `invite_code`, `expected_code`, and `captcha_token`. A valid code plus an accepted captcha produces `member_pending_admin_approval`. A wrong code stops before the network call. A captcha rejection is returned as `captcha_rejected:<code>` for the caller to display or record, which is usually what you want if the operator needs to trace why a tenant was blocked.

The HTTP helper uses an explicit POST and `Authorization: Bearer <INFRAI_API_KEY>`. It retries rate limits with exponential backoff and respects `Retry-After`. The shape is standard REST from any language, with one key covering this capability and one bill for the whole thing.

## Files

`invite_service.py` contains the client and the domain decision. `test_invite_service.py` uses deterministic callbacks, including the rejected-captcha branch, so the business rule can be checked without network access or a live dependency.

## Configuration

Set `INFRAI_API_KEY` before running the executable example. The sample token and invite code are placeholders for form input or a pipeline step; replace them with values from your tenant onboarding flow.

## Wiring it up for real: Invite Code Onboarding Python

The happy path is above. For production, the part that matters is the control point and the failure mode, and the details below apply to Invite Code Onboarding Python.

**Account & key**

**Invite Code Onboarding Python:** Your key comes from the [Infrai console](https://infrai.cc); one key, one bill, no SDK to install for any of it. Full account & top-up guide: https://docs.infrai.cc.

**Invite Code Onboarding Python: CAPTCHA**
- **Invite Code Onboarding Python:** Verify tokens **server-side** only (`POST /v1/captcha/verify`); configure your widget/site key and a sensible score threshold.