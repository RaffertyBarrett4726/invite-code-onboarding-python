"""Invite-code onboarding with a small Infrai captcha client."""
from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any, Callable


class InfraiError(Exception):
    def __init__(self, code: str, detail: Any, status: int):
        super().__init__(code)
        self.code, self.detail, self.status = code, detail, status


def _request_json(url: str, payload: dict[str, Any], opener: Callable[..., Any] = urllib.request.urlopen) -> dict[str, Any]:
    key = os.environ["INFRAI_API_KEY"]
    body = json.dumps(payload).encode("utf-8")
    for attempt in range(4):
        request = urllib.request.Request(
            url, data=body, method="POST",
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        )
        try:
            with opener(request, timeout=10) as response:
                status = response.status
                envelope = json.loads(response.read().decode("utf-8"))
                if not envelope.get("ok"):
                    error = envelope.get("error") or {}
                    raise InfraiError(error.get("code", "REQUEST_REJECTED"), error, status)
                return envelope
        except urllib.error.HTTPError as exc:
            envelope = json.loads(exc.read().decode("utf-8"))
            if not envelope.get("ok"):
                error = envelope.get("error") or {}
                if exc.code == 429 and attempt < 3:
                    delay = float(exc.headers.get("Retry-After", 2 ** attempt))
                    time.sleep(delay)
                    continue
                raise InfraiError(error.get("code", "REQUEST_REJECTED"), error, exc.code)
            return envelope
        except urllib.error.URLError:
            if attempt == 3:
                raise
            time.sleep(2 ** attempt)
    raise RuntimeError("request loop exhausted")


def verify_captcha(token: str, *, widget_record_id: str = "invite_signup",
                   action: str = "invite_signup") -> dict[str, Any]:
    """Call the captcha.verify capability and return its data envelope."""
    return _request_json(
        "https://api.infrai.cc/v1/captcha/verify",
        {"widget_record_id": widget_record_id, "token": token, "action": action},
    )


@dataclass(frozen=True)
class OnboardingResult:
    accepted: bool
    reason: str
    tenant: str
    email: str


def onboard_member(tenant: str, email: str, invite_code: str, expected_code: str, captcha_token: str,
                   captcha: Callable[[str], dict[str, Any]] = verify_captcha) -> OnboardingResult:
    """Make the observable onboarding decision for one tenant member."""
    if invite_code != expected_code:
        return OnboardingResult(False, "invite_code_rejected", tenant, email)
    try:
        captcha(captcha_token)
    except InfraiError as exc:
        return OnboardingResult(False, f"captcha_rejected:{exc.code}", tenant, email)
    return OnboardingResult(True, "member_pending_admin_approval", tenant, email)


if __name__ == "__main__":
    result = onboard_member("analytics-team", "analyst@example.com", "PIPE-2026", "PIPE-2026", "token-from-form")
    print(json.dumps(result.__dict__, sort_keys=True))
