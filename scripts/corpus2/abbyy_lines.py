"""Read an Internet Archive ABBYY OCR file (_abbyy.gz) into text lines with page and font size.

Plain string parsing, so it does not depend on the interpreter's expat; the format is machine-written and regular.
"""
import gzip
import html
import re

LINE = re.compile(r'<line\b([^>]*)>(.*?)</line>', re.S)
FMT = re.compile(r'<formatting\b([^>]*)>(.*?)</formatting>', re.S)
CHAR = re.compile(r'<charParams\b[^>]*?(?:/>|>(.*?)</charParams>)', re.S)
ATTR = re.compile(r'(\w+)="([^"]*)"')


def _lines(page):
    out = []
    for m in LINE.finditer(page):
        box = dict(ATTR.findall(m.group(1)))
        parts, sizes, ital = [], [], 0
        for f in FMT.finditer(m.group(2)):
            a = dict(ATTR.findall(f.group(1)))
            chars = html.unescape("".join(c or "" for c in CHAR.findall(f.group(2))))
            parts.append(chars)
            try:
                sizes += [float(a.get("fs", "0").rstrip("."))] * len(chars)
            except ValueError:
                pass
            if a.get("italic") in ("1", "true"):
                ital += len(chars)
        t = "".join(parts).rstrip()
        if t.strip():
            out.append({"text": t, "fs": sorted(sizes)[len(sizes) // 2] if sizes else 0.0, "italic": ital / len(t),
                        "l": int(box.get("l", 0)), "t": int(box.get("t", 0)), "r": int(box.get("r", 0)), "b": int(box.get("b", 0))})
    return out


def pages(path):
    """Yield (page_index, [line dict]) in order; a line has text, fs, italic, l, t, r, b."""
    buf, n = "", 0
    with gzip.open(path, "rt", encoding="utf-8", errors="replace") as f:
        while True:
            chunk = f.read(1 << 22)
            if not chunk:
                break
            buf += chunk
            while True:
                end = buf.find("</page>")
                if end < 0:
                    break
                yield n, _lines(buf[:end])
                n += 1
                buf = buf[end + 7:]


def body_lines(lines, tight=0.86):
    """Drop a page's footnotes.  They sit at the bottom with tighter leading than the text above them, so walk up from
    the last line while the gap between baselines stays tight.  Line height itself is no use: a line with no
    descenders looks short."""
    if len(lines) < 4:
        return lines
    gaps = [lines[i]["b"] - lines[i - 1]["b"] for i in range(1, len(lines))]
    pos = sorted(g for g in gaps if g > 0)
    if not pos:
        return lines
    body = pos[int(len(pos) * 0.7)]  # high enough that a long footnote cannot set the norm
    end = len(lines)
    while end > 1 and 0 < lines[end - 1]["b"] - lines[end - 2]["b"] < body * tight:
        end -= 1
    # the first footnote line is itself separated from the text by a wider gap, and belongs with the notes
    return lines[:end - 1] if end < len(lines) else lines
