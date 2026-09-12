#!/usr/bin/env python3
"""Generate `docs/assets/grain.png` — the D-5 grain tile, deterministically.

Why a file instead of an inline data-URI (DESIGN_SYSTEM.md §8.4 records the fallback): the
browser-level check that enforces "0 external runtime requests" treats a `data:` URL as a
request, so the tile ships as one small same-origin PNG instead. Still zero external requests,
still one fixed tile, still ≤ 0.03 effective alpha (the CSS applies `opacity`).

Usage: python3 tools/make_grain.py [--out docs/assets/grain.png] [--size 96]
"""

from __future__ import annotations

import argparse
import struct
import zlib
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


def chunk(tag: bytes, data: bytes) -> bytes:
    return (struct.pack(">I", len(data)) + tag + data
            + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF))


def make_png(size: int, seed: int = 20260912) -> bytes:
    """A size x size 8-bit RGB noise tile from a fixed LCG: byte-identical on every run."""
    state = seed
    rows = []
    for _y in range(size):
        row = bytearray()
        for _x in range(size):
            state = (1103515245 * state + 12345) & 0x7FFFFFFF
            row.append((state >> 16) & 0xFF)
        rows.append(bytes(row))
    ihdr = struct.pack(">IIBBBBB", size, size, 8, 2, 0, 0, 0)
    raw = b"".join(b"\x00" + row for row in rows)
    return (b"\x89PNG\r\n\x1a\n"
            + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", zlib.compress(raw, 9))
            + chunk(b"IEND", b""))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(REPO / "docs" / "assets" / "grain.png"))
    ap.add_argument("--size", type=int, default=96)
    args = ap.parse_args()
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    data = make_png(args.size)
    out.write_bytes(data)
    print(f"wrote {out} ({len(data)} bytes, {args.size}x{args.size} RGB noise)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
