"""build_argv: the sdl-freerdp command line for a CLI connection."""

from avd_feed_connect.rdp import build_argv, set_rdp_multimon


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


def _rdp(tmp_path, body):
    p = tmp_path / "x.rdp"
    p.write_text(body)
    return str(p)


def test_multimon_disable_rewrites_existing_property(tmp_path):
    # AVD feed .rdp ships "use multimon:i:1"; Single monitor must flip it to 0.
    path = _rdp(tmp_path, "full address:s:host\nuse multimon:i:1\nusername:s:u\n")
    set_rdp_multimon(path, False)
    lines = open(path).read().splitlines()
    assert "use multimon:i:0" in lines
    assert "use multimon:i:1" not in lines
    assert "full address:s:host" in lines  # other lines untouched


def test_multimon_enable_sets_one(tmp_path):
    path = _rdp(tmp_path, "use multimon:i:0\n")
    set_rdp_multimon(path, True)
    assert "use multimon:i:1" in open(path).read().splitlines()


def test_multimon_appends_when_absent(tmp_path):
    path = _rdp(tmp_path, "full address:s:host\n")
    set_rdp_multimon(path, False)
    assert "use multimon:i:0" in open(path).read().splitlines()


def test_multimon_missing_file_is_noop(tmp_path):
    set_rdp_multimon(str(tmp_path / "nope.rdp"), True)  # must not raise
