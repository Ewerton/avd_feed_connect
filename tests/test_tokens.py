"""TokenStore: the 0600-file fallback path (keyring is forced unavailable)."""

import json
import os
import stat

from avd_feed_connect.auth.tokens import TokenStore


def _file_only_store(tmp_path):
    """A TokenStore pinned to a temp cache file with libsecret disabled, so we
    exercise the plaintext-file fallback deterministically (no OS keyring)."""
    store = TokenStore(cache_path=str(tmp_path / "token-cache.json"))
    store._secret = lambda: None  # force keyring-unavailable branch
    return store


def test_save_then_load_round_trips(tmp_path):
    store = _file_only_store(tmp_path)
    store.save("refresh-abc")
    rec = store.load()
    assert rec is not None
    assert rec["refresh_token"] == "refresh-abc"
    assert isinstance(rec["obtained"], int)


def test_has_reflects_presence(tmp_path):
    store = _file_only_store(tmp_path)
    assert store.has() is False
    store.save("refresh-xyz")
    assert store.has() is True


def test_clear_removes_the_file(tmp_path):
    store = _file_only_store(tmp_path)
    store.save("refresh-xyz")
    store.clear()
    assert store.has() is False
    assert not os.path.exists(store._cache)


def test_cache_file_is_0600(tmp_path):
    store = _file_only_store(tmp_path)
    store.save("secret")
    mode = stat.S_IMODE(os.stat(store._cache).st_mode)
    assert mode == 0o600


def test_load_ignores_a_corrupt_file(tmp_path):
    store = _file_only_store(tmp_path)
    with open(store._cache, "w") as f:
        f.write("{not valid json")
    assert store.load() is None


def test_load_ignores_a_record_without_a_token(tmp_path):
    store = _file_only_store(tmp_path)
    with open(store._cache, "w") as f:
        json.dump({"obtained": 123}, f)
    assert store.load() is None
