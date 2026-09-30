"""Only the Entra login host may be loaded for FreeRDP's "Browse to:" prompt."""

import pytest

from avd_feed_connect import config


def test_accepts_entra_login():
    assert config.is_aad_login_url(
        "https://login.microsoftonline.com/common/oauth2/authorize?client_id=x")


@pytest.mark.parametrize("url", [
    "http://login.microsoftonline.com/x",
    "https://evil.example/x",
    "https://login.microsoftonline.com.evil.io/x",
    "https://evil.io/login.microsoftonline.com",
    "https://login.microsoftonline.com@evil.io/x",
    "https://microsoftonline.com/x",
    "file:///etc/passwd", "javascript:alert(1)", "",
])
def test_rejects_others(url):
    assert not config.is_aad_login_url(url)
