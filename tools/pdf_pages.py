#!/usr/bin/env python3
"""Report the page count of a Chrome-generated PDF (approximate: counts page objects).

A17 requires the printed index to show name, current role + employer and the LinkedIn URL on the
FIRST printed page; the page count itself is reported but is not a threshold. `pdftotext`/`pdfinfo`
are not installed in this environment, so the count is derived from the uncompressed object
structure Chrome writes.

Usage: python3 tools/pdf_pages.py <file.pdf> [...]
"""
import re
import sys
from pathlib import Path

for arg in sys.argv[1:]:
    data = Path(arg).read_bytes()
    pages = re.findall(rb"/Type\s*/Page[^s]", data)
    kids = re.findall(rb"/Count\s+(\d+)", data)
    print(f"{arg}: page objects={len(pages)} "
          f"declared /Count={[int(k) for k in kids] or 'n/a'} size={len(data)} bytes")
