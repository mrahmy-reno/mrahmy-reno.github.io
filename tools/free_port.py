#!/usr/bin/env python3
"""Print a free TCP port on the loopback interface — B2-04 / D13.

The B2-03 critique's D13: `tests/run_lighthouse.sh` hard-coded port 8123, so a reviewer running
their own probe on that port silently broke the Lighthouse step — the suite's own server failed to
bind, half the runs aborted with a Chrome interstitial, and the step reported a score computed from
two runs. Ports are now probed instead of assumed.

Stdlib only. Binds port 0, reads what the kernel assigned, closes, prints it.
"""

from __future__ import annotations

import socket
import sys


def free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


if __name__ == "__main__":
    try:
        print(free_port())
    except OSError as exc:                              # pragma: no cover - defensive
        print(f"could not find a free port: {exc}", file=sys.stderr)
        sys.exit(1)
