"""The bearer token is only ever sent to https Microsoft hosts."""

import pytest

from avd_feed_connect import config, http
from avd_feed_connect.gui import storage


@pytest.mark.parametrize("url", [
    "https://rdweb.wvd.microsoft.com/api/arm/feeddiscovery",
    "https://login.microsoftonline.com/common/oauth2/v2.0/token",
    "https://microsoft.com/x",
])
def test_trusted(url):
    assert config.is_trusted_url(url)


@pytest.mark.parametrize("url", [
    "http://rdweb.wvd.microsoft.com/x",            # not https
    "https://evilmicrosoft.com/x",                  # no dot boundary
    "https://microsoft.com.evil.io/x",              # suffix trick
    "https://evil.io/rdweb.wvd.microsoft.com",      # host in path
    "https://rdweb.wvd.microsoft.com@evil.io/x",    # userinfo trick
    "https://evil.io/?h=login.microsoftonline.com",
    "ftp://rdweb.wvd.microsoft.com/x",
    "", "not a url",
])
def test_untrusted(url):
    assert not config.is_trusted_url(url)


def _no_network(monkeypatch):
    def boom(*a, **k):
        raise AssertionError("request must not be sent")
    monkeypatch.setattr(http.urllib.request, "urlopen", boom)


def test_get_refuses_untrusted(monkeypatch):
    _no_network(monkeypatch)
    with pytest.raises(ValueError):
        http.get("https://evil.example/x", "secret-token")


def test_bearer_bytes_refuses_untrusted(monkeypatch):
    _no_network(monkeypatch)
    with pytest.raises(ValueError):
        storage.bearer_bytes("https://evil.example/icon.png", "secret-token")
