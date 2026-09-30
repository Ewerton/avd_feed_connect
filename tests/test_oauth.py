"""OAuthClient: PKCE helper, UPN extraction, silent refresh success/failure."""

import base64
import json

from avd_feed_connect import http
from avd_feed_connect.auth.oauth import OAuthClient, _b64url


class _FakeStore:
    def __init__(self, record=None):
        self.record = record
        self.saved = None

    def load(self):
        return self.record

    def save(self, refresh_token):
        self.saved = refresh_token


def _id_token(claims):
    """Build a minimal unsigned JWT (header.payload.sig) carrying ``claims``."""
    def seg(obj):
        raw = json.dumps(obj).encode()
        return base64.urlsafe_b64encode(raw).rstrip(b"=").decode()
    return f"{seg({'alg': 'none'})}.{seg(claims)}.sig"


def test_b64url_is_unpadded_urlsafe():
    out = _b64url(b"\xff\xff\xfe")
    assert "=" not in out and "+" not in out and "/" not in out


def test_set_upn_prefers_preferred_username():
    c = OAuthClient(_FakeStore())
    c.upn = ""
    tok = {"id_token": _id_token({"preferred_username": "sam@contoso.com",
                                  "email": "other@contoso.com"})}
    assert c.set_upn_from_token(tok) == "sam@contoso.com"
    assert c.upn == "sam@contoso.com"


def test_set_upn_does_not_override_a_pinned_upn():
    c = OAuthClient(_FakeStore())
    c.upn = "pinned@contoso.com"  # e.g. from AVD_UPN
    tok = {"id_token": _id_token({"preferred_username": "sam@contoso.com"})}
    assert c.set_upn_from_token(tok) == "pinned@contoso.com"


def test_set_upn_tolerates_a_missing_id_token():
    c = OAuthClient(_FakeStore())
    c.upn = ""
    assert c.set_upn_from_token({}) == ""


def test_get_token_silent_refresh(monkeypatch):
    store = _FakeStore({"refresh_token": "old-rt"})
    c = OAuthClient(store)
    monkeypatch.setattr(http, "post", lambda url, data: (200, {
        "access_token": "AT", "expires_in": 3600, "refresh_token": "new-rt",
        "id_token": _id_token({"preferred_username": "sam@contoso.com"}),
    }))
    assert c.get_token(verbose=False) == "AT"
    assert store.saved == "new-rt"          # rotated refresh token persisted
    assert c.upn == "sam@contoso.com"
    assert c.last_refresh_error == ""


def test_refresh_failure_records_reason(monkeypatch):
    c = OAuthClient(_FakeStore())
    monkeypatch.setattr(http, "post", lambda url, data: (400, {
        "error": "invalid_grant", "error_description": "AADSTS70043 expired"}))
    assert c._refresh("dead-rt") is None
    assert "invalid_grant" in c.last_refresh_error
    assert "AADSTS70043" in c.last_refresh_error
