#!/usr/bin/env python3
"""Debug helper: dump the table directory and the cmap table of a produced font."""
import struct
import sys
from pathlib import Path

data = Path(sys.argv[1]).read_bytes()
num = struct.unpack(">H", data[4:6])[0]
print("numTables", num, "searchRange", struct.unpack(">H", data[6:8])[0],
      "entrySelector", struct.unpack(">H", data[8:10])[0],
      "rangeShift", struct.unpack(">H", data[10:12])[0])
offsets = {}
for i in range(num):
    rec = 12 + i * 16
    tag = data[rec:rec + 4].decode("latin-1")
    chk, off, length = struct.unpack(">III", data[rec + 4:rec + 16])
    offsets[tag] = (off, length)
    print(f"  {tag!r:6} off={off:6} len={length:6} chk={chk:08x} end={off + length}")
cmap_off, cmap_len = offsets["cmap"]
c = data[cmap_off:cmap_off + cmap_len]
print("cmap version", struct.unpack(">H", c[0:2])[0], "numTables", struct.unpack(">H", c[2:4])[0])
plat, enc, sub_off = struct.unpack(">HHI", c[4:12])
print("record platform", plat, "encoding", enc, "offset", sub_off, "actual len", len(c))
sub = c[sub_off:]
fmt, length, lang, seg_x2 = struct.unpack(">HHHH", sub[0:8])
print("subtable format", fmt, "length", length, "language", lang, "segCountX2", seg_x2,
      "sub bytes", len(sub), "declared end", sub_off + length)
sr, es, rs = struct.unpack(">HHH", sub[8:14])
print("searchRange", sr, "entrySelector", es, "rangeShift", rs)
seg = seg_x2 // 2
print("expected searchRange", 2 * 2 ** (seg.bit_length() - 1))
p = 14
ends = struct.unpack(">%dH" % seg, sub[p:p + seg_x2]); p += seg_x2
print("reservedPad", struct.unpack(">H", sub[p:p + 2])[0]); p += 2
starts = struct.unpack(">%dH" % seg, sub[p:p + seg_x2]); p += seg_x2
deltas = struct.unpack(">%dh" % seg, sub[p:p + seg_x2]); p += seg_x2
ranges = struct.unpack(">%dH" % seg, sub[p:p + seg_x2]); p += seg_x2
print("bytes consumed", p, "of", len(sub))
for i in range(min(8, seg)):
    print(f"   seg{i}: {starts[i]:#06x}-{ends[i]:#06x} delta={deltas[i]} rangeOff={ranges[i]}")
print("   last:", f"{starts[-1]:#06x}-{ends[-1]:#06x} delta={deltas[-1]} rangeOff={ranges[-1]}")
print("   ends monotonic:", all(ends[i] < ends[i + 1] for i in range(len(ends) - 1)))
print("   starts <= ends:", all(starts[i] <= ends[i] for i in range(len(ends))))
