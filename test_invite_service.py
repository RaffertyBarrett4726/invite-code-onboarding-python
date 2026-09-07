from invite_service import InfraiError, OnboardingResult, onboard_member


def test_valid_invite_and_captcha_enters_pending_state():
    result = onboard_member("warehouse", "data@example.com", "ETL-42", "ETL-42", "captcha-token", lambda _: {"ok": True, "data": {}})
    assert result == OnboardingResult(True, "member_pending_admin_approval", "warehouse", "data@example.com")


def test_wrong_invite_does_not_call_captcha():
    called = []
    result = onboard_member("warehouse", "data@example.com", "BAD", "ETL-42", "captcha-token", lambda token: called.append(token))
    assert result.reason == "invite_code_rejected"
    assert called == []


def test_captcha_rejection_is_a_business_result():
    def reject(_: str):
        raise InfraiError("CAPTCHA_REJECTED", {}, 422)
    result = onboard_member("warehouse", "data@example.com", "ETL-42", "ETL-42", "captcha-token", reject)
    assert result.reason == "captcha_rejected:CAPTCHA_REJECTED"
