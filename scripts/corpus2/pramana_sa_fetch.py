"""Fetch (and cache) page metadata and all segments of every pramana_sa text. Rerunnable; cached."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pramana_sa_common import page, segments  # noqa: E402
from pramana_sa_texts import COMPARE, TEXTS  # noqa: E402

for path in list(TEXTS.values()) + list(COMPARE.values()):  # kept texts only
    page(path)
    segs = segments(path)
    print(path, len(segs), flush=True)
