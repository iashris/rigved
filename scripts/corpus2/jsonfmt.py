"""Load and save corpus JSON while keeping each file's own formatting (indent, ASCII escaping), so edits diff small."""

import json
import re


def load(path):
    raw = open(path, encoding="utf-8").read()
    m = re.match(r"\[\n( +)\{", raw)
    fmt = {"indent": len(m.group(1)) if m else None, "ensure_ascii": "\\u0" in raw[:200000],
           # one entry per line, as pramana_purana_convert writes: "[\n{...},\n{...}\n]"
           "lines": raw.startswith("[\n{")}
    return json.loads(raw), fmt


def save(path, data, fmt):
    fmt = dict(fmt)
    lines = fmt.pop("lines", False)
    with open(path, "w", encoding="utf-8") as f:
        if lines and isinstance(data, list):
            f.write("[\n" + ",\n".join(json.dumps(e, **fmt) for e in data) + "\n]\n")
        else:
            json.dump(data, f, **fmt)
