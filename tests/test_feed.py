"""FeedClient: discovery + tenant-feed XML is flattened into resource dicts."""

from avd_feed_connect import config, http
from avd_feed_connect.feed.discovery import FeedClient

_DISCOVERY_XML = """<?xml version="1.0"?>
<TenantFeedURLs>
  <TenantFeedURL FeedURL="https://feed.example/f0" TenantId="t1"
                 TenantDisplayName="Contoso"/>
</TenantFeedURLs>"""

_FEED_XML = """<?xml version="1.0"?>
<ResourceCollection>
  <Publisher Name="Contoso IT">
    <Resources>
      <Resource ID="r1" Title="Finance Desktop" Type="Desktop" ArmPath="/arm/1">
        <HostingTerminalServers><HostingTerminalServer>
          <ResourceFile URL="https://feed.example/r1.rdp"/>
        </HostingTerminalServer></HostingTerminalServers>
        <Icon32 FileURL="https://feed.example/r1.png"/>
      </Resource>
      <Resource ID="r2" Title="Ops Console" Type="RemoteApp" ArmPath="/arm/2">
        <HostingTerminalServers><HostingTerminalServer>
          <ResourceFile URL="https://feed.example/r2.rdp"/>
        </HostingTerminalServer></HostingTerminalServers>
      </Resource>
    </Resources>
  </Publisher>
</ResourceCollection>"""


def test_enumerate_flattens_resources(monkeypatch, tmp_path):
    monkeypatch.setattr(config, "OUT", str(tmp_path))  # raw XML dumps go to tmp

    def fake_get(url, token, accept="*/*"):
        body = _DISCOVERY_XML if url == config.DISCOVERY else _FEED_XML
        return 200, {}, body

    monkeypatch.setattr(http, "get", fake_get)

    resources = FeedClient().enumerate("token")
    assert len(resources) == 2

    desktop = resources[0]
    assert desktop["id"] == "r1"
    assert desktop["title"] == "Finance Desktop"
    assert desktop["type"] == "Desktop"
    assert desktop["publisher"] == "Contoso IT"
    assert desktop["tenant"] == "Contoso"
    assert desktop["rdp_url"] == "https://feed.example/r1.rdp"
    assert desktop["icon32"] == "https://feed.example/r1.png"

    remoteapp = resources[1]
    assert remoteapp["type"] == "RemoteApp"
    assert remoteapp["icon32"] is None  # no Icon32 element on this resource
