#!/usr/bin/env python3
"""Backwards-compatible command-line shim.

The feed/auth/connect implementation now lives in the ``avd_feed_connect``
package (installed next to this file). This shim just forwards to its CLI entry
point so ``avdfeed.py <cmd>`` keeps working for development and scripting.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from avd_feed_connect.cli import main  # noqa: E402

if __name__ == "__main__":
    main()
