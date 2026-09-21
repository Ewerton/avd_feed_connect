"""Download a resource's ready-to-use .rdp file from its feed ResourceFile URL."""

import os
import re
import sys

from .. import config, http


def download_rdp(token, res):
    """Fetch resource ``res``'s .rdp text and write it under the feed data dir,
    returning the path. ``res`` is a resource dict from the feed."""
    if not res["rdp_url"]:
        sys.exit(f"resource {res['title']!r} has no ResourceFile URL")
    st, _, rdp = http.get(res["rdp_url"], token)
    if st != 200:
        sys.exit(f"rdp download failed ({st}): {rdp[:300]}")
    os.makedirs(config.OUT, exist_ok=True)
    safe = re.sub(r"[^A-Za-z0-9._-]+", "_", res["title"])[:80]
    path = os.path.join(config.OUT, safe + ".rdp")
    with open(path, "w") as f:
        f.write(rdp)
    return path
