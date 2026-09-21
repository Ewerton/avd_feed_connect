"""build_argv: the sdl-freerdp command line for a CLI connection."""

from avd_feed_connect.rdp import build_argv


def test_argv_core_flags():
    argv = build_argv("/app/bin/sdl-freerdp", "/tmp/x.rdp", "")
    assert argv[0] == "/app/bin/sdl-freerdp"
    assert argv[1] == "/tmp/x.rdp"
    assert "/gateway:type:arm" in argv
    assert "/sec:aad" in argv
    assert "/f" in argv
    assert "-multimon" in argv


def test_argv_includes_user_when_upn_set():
    argv = build_argv("sdl-freerdp", "x.rdp", "sam@contoso.com")
    assert "/u:sam@contoso.com" in argv


def test_argv_omits_user_when_no_upn():
    argv = build_argv("sdl-freerdp", "x.rdp", "")
    assert not any(a.startswith("/u:") for a in argv)
