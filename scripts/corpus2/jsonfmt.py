"""Load and save corpus JSON while keeping each file's own formatting (indent, ASCII escaping), so edits diff small."""

import json
import re


def load(path):
    raw = open(path, encoding="utf-8").read()
    m = re.match(r"\[\n( +)\{", raw)
    fmt = {"indent": len(m.group(1)) if m else None, "ensure_ascii": "\\u0" in raw[:200000]}
    return json.loads(raw), fmt


def save(path, data, fmt):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, **fmt)
